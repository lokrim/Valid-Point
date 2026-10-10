"""Run only the bounded R03 mini_7 development demonstration."""
from __future__ import annotations

import csv
from dataclasses import asdict, replace
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

import numpy as np

from valid_point.attacks.manifests import Attempt, file_sha256
from valid_point.attacks.overlays import (FAMILIES, SEED, apply_overlay,
                                          cell_index, freeze_target, seed_key)
from valid_point.development_scores import AlarmDecision, decide, fit_exploratory, normalize_raw
from valid_point.io.mixed_signals import read_pcd, write_pcd
from valid_point.replay import AllowedSource, CloudEvent, ReplayConfig, replay
from valid_point.temporal import TemporalEWMA

ROOT=Path(__file__).resolve().parents[1]
ARMS=("D-only","G-only","max(D,G)")


def save_table(run: Path, name: str, rows: list[dict]) -> None:
    path=run/(name+".csv")
    columns=list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w",newline="") as output:
        writer=csv.DictWriter(output,fieldnames=columns); writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list,tuple)) else v for k,v in row.items()})
    with (run/(name+".md")).open("w") as output:
        output.write(f"# {name}\n\nRows: {len(rows)}. Full rows are in [{name}.csv]({name}.csv).\n\n")
        output.write("| "+" | ".join(columns)+" |\n| "+" | ".join("---" for _ in columns)+" |\n")
        for row in rows:
            output.write("| "+" | ".join(str(row.get(k,"" )).replace("|","\\|").replace("\n"," ") for k in columns)+" |\n")


def selected_schedule(elapsed: float, schedule: str, cfg: dict) -> bool:
    return any(start <= elapsed < end for start,end in cfg["schedules_s"][schedule])


def score_arm(raw_rows, refs, episode: str, tau: float, g_reset: float, first_ns: int):
    state=TemporalEWMA(tau,g_reset)
    rows=[]
    for raw in raw_rows:
        norm=normalize_raw(raw,refs,"R03.exploratory.mini_7.v1")
        for arm in ARMS:
            decision=decide(raw,norm,arm)
            temporal=state.update(episode=episode,principal=raw.principal,sensor=raw.stream,
                                  method_arm=arm,reference_version=decision.reference_id,
                                  source_ns=raw.source_ns,A=decision.A,reason=decision.reason)
            alarm=AlarmDecision(raw.cloud_id,raw.stream,raw.principal,raw.source_ns,arm,
                                "unknown",None,None,None,"DIAGNOSTIC_CALIBRATION_UNAVAILABLE",
                                decision.reference_id)
            rows.append({"episode":episode,"cloud_id":raw.cloud_id,"stream":raw.stream,
                         "principal":raw.principal,"source_ns":raw.source_ns,
                         "elapsed_s":(raw.source_ns-first_ns)/1e9,"sync_id":raw.sync_id,
                         "arm":arm,"raw_D_counts":raw.density.counts,"raw_D_inside_points":sum(raw.density.counts) if raw.density.counts else None,
                         "raw_G_m":raw.geometry.distance_m,"raw_G_reason":raw.geometry.reason,
                         "pose_age_s":raw.pose_age_s,"G_gap_s":raw.geometry.gap_s,
                         "D_anomaly":norm.d,"G_anomaly":norm.g,"D_reason":norm.d_reason,
                         "G_reason":norm.g_reason,"D_contexts":norm.d_contexts,"G_context":norm.g_context,
                         "A":decision.A,"C":decision.C,"score_status":decision.status,
                         "score_reason":decision.reason,"Z":temporal.Z,"C_time":temporal.C_time,
                         "held_Z":temporal.held_Z,"held_age_s":temporal.held_age_s,
                         "state_status":temporal.status,"state_reason":temporal.reason,
                         "state_ready":temporal.ready,"state_updates":temporal.eligible_updates,
                         "contiguous_s":temporal.contiguous_s,"state_reset":temporal.reset,
                         "instant_alarm":alarm.instant_alarm,"temporal_alarm":alarm.temporal_alarm,
                         "threshold_id":alarm.threshold_id,"alarm_reason":alarm.reason})
    return rows,state.checkpoint()


def _reader_values(path: Path) -> np.ndarray:
    with path.open("rb") as handle:
        _, values=read_pcd(handle)
    return values


def _benign(values: np.ndarray, name: str, key: str, cfg: dict) -> np.ndarray:
    result=values.copy()
    if name=="noise":
        rng=np.random.default_rng(int(key[:16],16))
        result[:,:3]+=rng.normal(0,cfg["benign_executed"]["coordinate_noise_sigma_m"],size=(len(result),3)).astype(np.float32)
    return result


def _pose_control(poses: dict, cfg: dict):
    from math import cos,sin,radians
    theta=radians(cfg["benign_executed"]["calibration_yaw_deg"])
    c,s=cos(theta),sin(theta)
    perturb=np.eye(4); perturb[:3,:3]=[[c,-s,0],[s,c,0],[0,0,1]]
    perturb[0,3]=cfg["benign_executed"]["calibration_translation_m"]
    skew=int(cfg["benign_executed"]["source_clock_skew_ms"]*1_000_000)
    copy={k:list(v) for k,v in poses.items()}
    copy["003"]=[replace(p,matrix=p.matrix@perturb if p.matrix is not None else None,
                          available_ns=p.available_ns+skew) for p in poses["003"]]
    return copy


def main():
    cfg=json.loads((ROOT/"configs/development_replay.json").read_text())
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run=ROOT/"artifacts"/(stamp+"-R03")
    run.mkdir(parents=True,exist_ok=False)
    t0=time.monotonic(); cpu0=time.process_time()
    log=[]
    def note(message):
        line=f"{datetime.now(timezone.utc).isoformat()} {message}"
        log.append(line); print(line,flush=True); (run/"execution.log").write_text("\n".join(log)+"\n")
    try:
        (run/"config.json").write_text(json.dumps(cfg,indent=2)+"\n")
        rawroot=ROOT/"data/mixed_signals"/cfg["revision"]/"raw"
        clouds=rawroot/"PointClouds/mini_7"; posepath=rawroot/"Odometry/mini_7"
        source=AllowedSource(clouds,posepath)
        events=source.events(max_sync_id=cfg["max_sync_id"],first_seconds=cfg["first_seconds"])
        first_ns=min(e.source_ns for e in events)
        if not events or max((e.source_ns-first_ns)/1e9 for e in events)<24:
            raise RuntimeError("required 25 s clean coverage missing")
        if len({e.stream for e in events})!=5 or not any(e.stream=="003" for e in events):
            raise RuntimeError("missing required clean companions or primary sender")
        poses={s:source.read_poses(s) for s in ("003","004","laser")}
        rcfg=ReplayConfig()
        note(f"clean replay {len(events)} real PCD events")
        clean=list(replay(events,source,config=rcfg,poses=poses))
        import pickle
        with (run/"clean_raw_cache.pkl").open("xb") as handle:
            pickle.dump(clean,handle,protocol=5)
        base_hash={r.cloud_id:r.input_sha256 for r in clean}
        if any(v is None for v in base_hash.values()):
            raise RuntimeError("clean production reader rejected a base cloud")
        fit=[r for r in clean if 0 <= (r.source_ns-first_ns)/1e9 < 10]
        refs=fit_exploratory(fit,segment="mini_7",reference_id="R03.exploratory.mini_7.v1")
        save_table(run,"T_R03_references",[asdict(x) for x in refs.values()])
        note(f"exploratory first-10s reference contexts {len(refs)}")
        clean_rows,clean_state=score_arm(clean,refs,"clean",1.,.5,first_ns)
        # Per stream and arm, subsequent clean support is <200 in this bounded window.
        calibration=[]
        for stream in sorted({e.stream for e in events}):
            for arm in ARMS:
                sample=[r for r in clean_rows if r["stream"]==stream and r["arm"]==arm and 10<=r["elapsed_s"]<25]
                known=sum(r["A"] is not None for r in sample)
                ready=sum(r["state_ready"] and r["Z"] is not None for r in sample)
                calibration.append({"stream":stream,"arm":arm,"segment":"mini_7",
                                    "clean_window_s":"[10,25)","attempted":len(sample),
                                    "instant_known":known,"temporal_ready_known":ready,
                                    "minimum_known":200,"instant_threshold":None,"temporal_threshold":None,
                                    "status":"UNAVAILABLE_INSUFFICIENT_KNOWN" if known<200 or ready<200 else "REQUIRES_ORDER_STATISTIC"})
        if any(x["status"]=="REQUIRES_ORDER_STATISTIC" for x in calibration):
            raise RuntimeError("calibration support unexpectedly reaches rule; implement separate thresholds")
        save_table(run,"T_R03_calibration",calibration)
        tau_checks={"candidate_tau_s":1.,"g_reset_s":.5,"basis":"clean source coverage and 5 s prefix; no attack outcomes",
                    "clean_duration_s":max((r.source_ns-first_ns)/1e9 for r in clean),
                    "eligible_003_D":sum(r["A"] is not None for r in clean_rows if r["stream"]=="003" and r["arm"]=="D-only"),
                    "first_003_D_ready_s":next((r["elapsed_s"] for r in clean_rows if r["stream"]=="003" and r["arm"]=="D-only" and r["state_ready"]),None)}
        tau_checks["warmup_feasible_before_onset"] = (tau_checks["first_003_D_ready_s"] is not None
                                                       and tau_checks["first_003_D_ready_s"] < 5)
        # A missing/degenerate exploratory scale remains unknown rather than
        # triggering an attack-curve-driven tau change.
        (run/"tau_choice.json").write_text(json.dumps(tau_checks,indent=2)+"\n")
        np.savez_compressed(run/"clean_003_example.npz",values=_reader_values(next(e.path for e in events if e.stream=="003" and e.sync_id==75)))
        prediction_dir=run/"sealed_predictions"; prediction_dir.mkdir()
        save_table(prediction_dir,"clean_scores",clean_rows)
        (prediction_dir/"clean_state.json").write_text(json.dumps(clean_state,indent=2)+"\n")
        # Target is frozen from the first three seconds of the sender only.
        prefix=[(e.cloud_id,_reader_values(e.path)) for e in events if e.stream=="003" and (e.source_ns-first_ns)/1e9<3]
        target=freeze_target(prefix)
        (run/"target.json").write_text(json.dumps(asdict(target),indent=2)+"\n")
        attempts=[]; roundtrip=[]; summaries=[]
        sender_events=[e for e in events if e.stream=="003"]
        clean_by_id={r.cloud_id:r for r in clean}
        # Every identity control is written/reloaded through the production PCD reader.
        identity_dir=run/"identity_controls"; identity_dir.mkdir()
        identity_event=next(e for e in sender_events if 5 <= (e.source_ns-first_ns)/1e9 < 15)
        identity_values=_reader_values(identity_event.path)
        for family in FAMILIES:
            key=seed_key("mini_7","003",identity_event.cloud_id,family,0.,SEED)
            overlay=apply_overlay(identity_values,family=family,severity=0.,key=key,target=target)
            path=identity_dir/(family+".pcd")
            write_pcd(path,overlay.values)
            reread=_reader_values(path)
            maximum=float(np.max(np.abs(reread-identity_values))) if len(reread) else 0.
            roundtrip.append({"family":family,"cloud_id":identity_event.cloud_id,"base_sha256":base_hash[identity_event.cloud_id],
                              "derived_sha256":file_sha256(path),"base_count":len(identity_values),"reread_count":len(reread),
                              "max_abs_field_error":maximum,"tolerance":1e-6,"status":"PASS" if maximum<=1e-6 else "FAIL"})
        save_table(run,"T_R03_roundtrip",roundtrip)
        note("five PCD identity controls reloaded")
        specs=list(cfg["episodes"])+[{"family":"noise","severity":cfg["benign_executed"]["coordinate_noise_sigma_m"],"schedule":"sustained"},
                                      {"family":"calibration_timing","severity":0.,"schedule":"sustained"}]
        for number,spec in enumerate(specs):
            family=spec["family"]; severity=spec["severity"]; schedule=spec["schedule"]
            episode="arm_"+sha256(f"{number}:{family}:{severity}:{schedule}:{SEED}".encode()).hexdigest()[:12]
            active=run/"active_derived"; active.mkdir(exist_ok=False)
            selection_dir=run/"selection_ledgers"/episode
            selection_dir.mkdir(parents=True,exist_ok=False)
            changed_events=[]; episode_attempts=[]; example=None
            note(f"episode {number+1}/{len(specs)} {family} {schedule}")
            for event in sender_events:
                elapsed=(event.source_ns-first_ns)/1e9
                if not selected_schedule(elapsed,schedule,cfg) or family=="calibration_timing":
                    changed_events.append(event)
                    continue
                original=_reader_values(event.path)
                key=seed_key("mini_7","003",event.cloud_id,family if family!="noise" else "displacement",severity,SEED)
                overlay=None; path=active/event.cloud_id
                try:
                    overlay=_benign(original,family,key,cfg) if family=="noise" else apply_overlay(original,family=family,severity=severity,key=key,target=target)
                    values=overlay if isinstance(overlay,np.ndarray) else overlay.values
                    write_pcd(path,values)
                    reloaded=_reader_values(path)  # same production reader as clean
                    digest=file_sha256(path)
                    n=min(len(original),len(reloaded))
                    changed=int(abs(len(original)-len(reloaded))+np.count_nonzero(np.any(original[:n]!=reloaded[:n],axis=1)))
                    oldcells=np.bincount(cell_index(original[:,:3],(0.,0.))[cell_index(original[:,:3],(0.,0.))>=0],minlength=32)
                    newindex=cell_index(reloaded[:,:3],(0.,0.))
                    newcells=np.bincount(newindex[newindex>=0],minlength=32)
                    cellchanges=int(np.abs(newcells-oldcells).sum())
                    maxdist=float(np.linalg.norm(reloaded[:n,:3]-original[:n,:3],axis=1).max()) if n and len(original)==len(reloaded) else None
                    inside=float(np.mean(newindex>=0)) if len(reloaded) else None
                    status="accepted"; why="VALID"
                    changed_events.append(replace(event,path=path))
                    if example is None and event.sync_id>=75:
                        example=(original,reloaded,event.cloud_id)
                except (ValueError,OSError,UnicodeError) as exc:
                    digest=file_sha256(path) if path.exists() else None
                    reloaded=None; changed=None; cellchanges=None; maxdist=None; inside=None
                    status="rejected"; why=type(exc).__name__+":"+str(exc)
                    changed_events.append(replace(event,path=path if path.exists() else None,state="present" if path.exists() else "absent"))
                selected=() if family=="noise" or overlay is None else overlay.selected_ids
                changed_ids=() if family=="noise" or overlay is None else overlay.changed_ids
                failed=() if family=="noise" or overlay is None else overlay.failed_ids
                intended=len(original) if family=="noise" else overlay.intended_count if overlay is not None else 0
                ledger=selection_dir/(event.cloud_id+".npz")
                np.savez_compressed(ledger,selected_ids=np.asarray(selected,dtype=np.int32),
                                    changed_ids=np.asarray(changed_ids,dtype=np.int32),
                                    failed_ids=np.asarray(failed,dtype=np.int32),
                                    assigned_additions=values[len(original):] if overlay is not None and family=="addition" else np.empty((0,4),dtype=np.float32))
                attempt=Attempt(episode,event.cloud_id,family,severity,schedule,event.source_ns,
                                base_hash[event.cloud_id],key,target.cell_id,intended,len(selected),len(changed_ids),len(failed),
                                overlay.reason if overlay is not None and family!="noise" else "BENIGN_NOISE" if family=="noise" else "GENERATOR_REJECTED",
                                str(ledger.relative_to(run)),file_sha256(ledger),
                                len(values) if overlay is not None else 0,digest,status,why,
                                len(reloaded) if reloaded is not None else None,changed,cellchanges,maxdist,inside)
                episode_attempts.append(attempt)
            note(f"episode {number+1}: wrote and production-reloaded {len(episode_attempts)} derived PCDs")
            # Recompute sender G from this arm's own prior clouds. Companions have
            # no peer-dependent factors and retain clean raw records byte-for-byte.
            active_source=AllowedSource(clouds,posepath,active)
            armposes=_pose_control(poses,cfg) if family=="calibration_timing" else poses
            attacked_sender=list(replay(changed_events,active_source,config=rcfg,poses=armposes))
            note(f"episode {number+1}: sender replay complete; G unknown {sum(r.geometry.status!='known' for r in attacked_sender)}/{len(attacked_sender)}")
            attacked_map={r.cloud_id:r for r in attacked_sender}
            full=[attacked_map[r.cloud_id] if r.stream=="003" else r for r in clean]
            prediction,checkpoint=score_arm(full,refs,episode,1.,.5,first_ns)
            save_table(prediction_dir,episode+"_scores",prediction)
            (prediction_dir/(episode+"_state.json")).write_text(json.dumps(checkpoint,indent=2)+"\n")
            pred_hash=file_sha256(prediction_dir/(episode+"_scores.csv"))
            if example is not None:
                np.savez_compressed(run/(episode+"_geometry.npz"),clean=example[0],derived=example[1],cloud_id=example[2])
                if family=="rearrangement":
                    with np.load(selection_dir/(example[2]+".npz")) as ids:
                        failed_example=ids["failed_ids"].copy()
                    np.savez_compressed(run/"F_R03_corrected_rearrangement_example.npz",
                                        clean=example[0],derived=example[1],
                                        failed_ids=failed_example,cloud_id=example[2])
            attempts.extend(x.as_dict() for x in episode_attempts)
            summaries.append({"episode":episode,"family":family,"severity":severity,"schedule":schedule,
                              "sender_events":len(sender_events),"companion_events":len(events)-len(sender_events),
                              "scheduled_events":sum(selected_schedule((e.source_ns-first_ns)/1e9,schedule,cfg) for e in sender_events),
                              "written_derived":len(episode_attempts),"accepted":sum(x.reader_status=="accepted" for x in episode_attempts),
                              "rejected":sum(x.reader_status=="rejected" for x in episode_attempts),
                              "zero_realized":sum(x.realized_changed_rows==0 for x in episode_attempts),
                              "prediction_sha256":pred_hash,"checkpoint_sha256":file_sha256(prediction_dir/(episode+"_state.json"))})
            shutil.rmtree(active)
        save_table(run,"T_R03_attempts",attempts)
        save_table(run,"T_R03_episode_flow",summaries)
        # Check originals and every honest companion after all overlay writes.
        post={e.cloud_id:file_sha256(e.path) for e in events}
        immutability={"all_base_identical":post==base_hash,
                      "honest_companion_count":sum(e.stream!="003" for e in events),
                      "honest_companions_identical":all(post[e.cloud_id]==base_hash[e.cloud_id] for e in events if e.stream!="003")}
        (run/"immutability.json").write_text(json.dumps(immutability,indent=2)+"\n")
        prediction_hashes={p.name:file_sha256(p) for p in prediction_dir.iterdir() if p.is_file()}
        (run/"prediction_seal.json").write_text(json.dumps(prediction_hashes,indent=2)+"\n")
        # All interval annotations below are evaluator-only and written after seal.
        (run/"evaluator_intervals.json").write_text(json.dumps({"episodes":specs,"schedules_s":cfg["schedules_s"],
                                                      "prediction_seal_sha256":file_sha256(run/"prediction_seal.json")},indent=2)+"\n")
        for script in ("summarize_r03_evidence.py","export_r03_records.py","check_r03_boundary.py"):
            result=subprocess.run([sys.executable,str(ROOT/"scripts"/script),str(run)],cwd=ROOT,
                                  env={**os.environ,"PYTHONPATH":str(ROOT/"src")},capture_output=True,text=True)
            (run/(script+".log")).write_text(result.stdout+result.stderr)
            if result.returncode:
                raise RuntimeError(f"{script} failed: {result.stderr[-2000:]}")
        state_checks=[{"check":"all_base_identical", "pass":immutability["all_base_identical"]},
                      {"check":"honest_companions_identical","pass":immutability["honest_companions_identical"]},
                      {"check":"identity_read_write_tol","pass":all(r["status"]=="PASS" for r in roundtrip)},
                      {"check":"all_derived_reader_accepted","pass":all(r["reader_status"]=="accepted" for r in attempts)},
                      {"check":"calibration_unavailable","pass":all(r["status"]=="UNAVAILABLE_INSUFFICIENT_KNOWN" for r in calibration)}]
        save_table(run,"T_R03_state_checks",state_checks)
        note("predictions sealed, evaluator intervals joined only offline")
        test=subprocess.run([sys.executable,"-m","pytest","-q","tests/test_overlays.py","tests/test_temporal.py","tests/test_replay_isolation.py","--junitxml="+str(run/"test_results.xml")],
                            cwd=ROOT,env={**os.environ,"PYTHONPATH":str(ROOT/"src")},capture_output=True,text=True)
        (run/"test.log").write_text(test.stdout+test.stderr)
        note(f"R03 tests exit {test.returncode}")
        import nbformat
        from nbclient import NotebookClient
        nb=nbformat.read(ROOT/"notebooks/R03_replay_temporal.ipynb",as_version=4)
        os.environ["VP_RUN_DIR"]=str(run)
        notebook_error=None
        try:
            nb=NotebookClient(nb,timeout=900,kernel_name="python3",resources={"metadata":{"path":str(ROOT)}}).execute()
        except Exception as exc:
            notebook_error=repr(exc)
            (run/"notebook_error.txt").write_text(notebook_error+"\n")
        nbformat.write(nb,run/"R03_replay_temporal.executed.ipynb")
        note(f"fresh notebook {'passed' if notebook_error is None else 'failed'}")
        status="PASS" if test.returncode==0 and notebook_error is None and all(x["pass"] for x in state_checks) else "BLOCKED"
        environment={"python":sys.version,"numpy":np.__version__,"platform":sys.platform,
                     "cpu_s":time.process_time()-cpu0,"wall_s":time.monotonic()-t0,
                     "peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                     "free_disk_bytes":shutil.disk_usage(ROOT).free}
        (run/"environment.json").write_text(json.dumps(environment,indent=2)+"\n")
        (run/"access.log").write_text("\n".join(source.access_log)+"\n")
        (run/"gate.md").write_text(f"# GR3 — R03 development replay gate\n\nTechnical status: **{status}**. Scientific outcome: development-only, uncalibrated.\n\n"
                                   f"{len(events)} clean events, {len(summaries)} matched episode arms, {len(attempts)} derived attempt rows. "
                                   "Five zero-severity writer/reloader controls. Threshold alarms remain null under the unchanged >=200 known rule; "
                                   "one mini_7 scene and internal time blocks do not establish independent calibration. "
                                   "No attack-curve sign is required. See attempt/roundtrip/state tables, figures, test report, notebook and prediction seal.\n")
        source_files=[ROOT/p for p in ("src/valid_point/io/mixed_signals.py","src/valid_point/replay.py",
                       "src/valid_point/evidence/temporal_geometry.py",
                       "src/valid_point/attacks/overlays.py","src/valid_point/attacks/manifests.py",
                       "src/valid_point/temporal.py","src/valid_point/development_scores.py",
                       "scripts/replay_development.py","scripts/summarize_r03_evidence.py",
                       "scripts/export_r03_records.py",
                       "scripts/check_r03_boundary.py","scripts/validate_r03_run.py",
                       "scripts/repair_r03_rearrangement.py","configs/development_replay.json",
                       "notebooks/R03_replay_temporal.ipynb","tests/test_overlays.py",
                       "tests/test_temporal.py","tests/test_replay_isolation.py")]
        manifest={"run_id":run.name,"stage":"R03","status":status,"config_sha256":file_sha256(ROOT/"configs/development_replay.json"),
                  "seed":SEED,"source_sha256":{str(p.relative_to(ROOT)):file_sha256(p) for p in source_files},
                  "input_sha256":base_hash,"pose_csv_sha256":{s:file_sha256(posepath/f"odometry_{s}.csv") for s in poses},
                  "archive_sha256":cfg["archive_sha256"],"split_lineage":cfg["split_lineage"],
                  "reference_id":"R03.exploratory.mini_7.v1","calibration_id":None,
                  "git_head":subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
                  "git_dirty":subprocess.run(["git","status","--short"],cwd=ROOT,capture_output=True,text=True).stdout,
                  "output_sha256":{str(p.relative_to(run)):file_sha256(p) for p in run.rglob("*") if p.is_file() and p.name!="manifest.json"}}
        (run/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        note(f"GR3 {status}: {run}")
    except Exception as exc:
        (run/"failure.txt").write_text(repr(exc)+"\n")
        note(f"FAILED {type(exc).__name__}: {exc}")
        raise


if __name__=="__main__": main()
