"""Preserve invalid development attempt and repair the same R03 rearrangement case."""
from __future__ import annotations

import csv
from dataclasses import asdict, replace
from hashlib import sha256
import json
from pathlib import Path
import pickle
import shutil
import sys

import numpy as np

from valid_point.attacks.manifests import Attempt, file_sha256
from valid_point.attacks.overlays import Target, apply_overlay, cell_index
from valid_point.development_scores import ExploratoryReference
from valid_point.io.mixed_signals import read_pcd, write_pcd
from valid_point.replay import AllowedSource, ReplayConfig, replay

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay_development import save_table, score_arm


def load_rows(path):
    with path.open(newline="") as f: return list(csv.DictReader(f))


def read_values(path):
    with path.open("rb") as f: return read_pcd(f)[1]


def main(run: Path):
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((run/"config.json").read_text())
    flows=load_rows(run/"T_R03_episode_flow.csv")
    flow=next(x for x in flows if x["family"]=="rearrangement" and x["schedule"]=="sustained")
    episode=flow["episode"]
    old=load_rows(run/"T_R03_attempts.csv")
    invalid=[r for r in old if r["episode"]==episode]
    if len(invalid)!=100: raise RuntimeError("unexpected invalid attempt support")
    deviation=run/"protocol_deviation"; deviation.mkdir(exist_ok=False)
    save_table(deviation,"invalid_rearrangement_attempts",invalid)
    shutil.copytree(run/"selection_ledgers"/episode,deviation/"invalid_selection_ledgers")
    pred=run/"sealed_predictions"
    for suffix in ("_scores.csv","_scores.md","_state.json"):
        shutil.copy2(pred/(episode+suffix),deviation/(episode+suffix))
    (deviation/"reason.md").write_text(
        "# Invalid first rearrangement execution\n\n"
        "The original validity check accepted outside-D-crop rows when both original and proposed cell IDs were -1. "
        "That violates the declared within-original-D-cell rule. This executed attempt, its selected IDs, "
        "reader hashes and prediction are retained here and excluded from the corrected development demonstration. "
        "The fix requires original cell ID >=0 before any proposed move. No severity, target, seed, window, "
        "reference or threshold changed.\n")
    rawroot=root/"data/mixed_signals"/cfg["revision"]/"raw"
    clouds=rawroot/"PointClouds/mini_7"; poses=rawroot/"Odometry/mini_7"
    source=AllowedSource(clouds,poses)
    events=source.events(max_sync_id=cfg["max_sync_id"],first_seconds=cfg["first_seconds"])
    first_ns=min(e.source_ns for e in events)
    sender=[e for e in events if e.stream=="003"]
    target_data=json.loads((run/"target.json").read_text())
    target=Target(target_data["cell_id"],tuple(target_data["center_xyz_m"]) if target_data["center_xyz_m"] else None,
                  tuple(target_data["prefix_cloud_ids"]),target_data["prefix_point_count"])
    old_by_id={r["cloud_id"]:r for r in invalid}
    active=run/"active_corrected"; active.mkdir(exist_ok=False)
    selection=run/"selection_ledgers"/episode
    repaired=[]; arm_events=[]
    for event in sender:
        elapsed=(event.source_ns-first_ns)/1e9
        if not 5<=elapsed<15:
            arm_events.append(event); continue
        prior=old_by_id[event.cloud_id]
        values=read_values(event.path)
        overlay=apply_overlay(values,family="rearrangement",severity=1.,key=prior["seed_key"],target=target)
        path=active/event.cloud_id
        write_pcd(path,overlay.values)
        reread=read_values(path)
        if len(reread)!=len(values) or not np.array_equal(np.bincount(cell_index(values[:,:3],(0.,0.))[cell_index(values[:,:3],(0.,0.))>=0],minlength=32),
                                                          np.bincount(cell_index(reread[:,:3],(0.,0.))[cell_index(reread[:,:3],(0.,0.))>=0],minlength=32)):
            raise RuntimeError("corrected rearrangement broke cell counts")
        original_cells=cell_index(values[:,:3],(0.,0.))
        if any(original_cells[list(overlay.changed_ids)]<0):
            raise RuntimeError("outside-D row moved after correction")
        changed=int(np.count_nonzero(np.any(values!=reread,axis=1)))
        distance=np.linalg.norm(reread[:,:3]-values[:,:3],axis=1)
        existing=selection/(event.cloud_id+".npz")
        existing.unlink()
        np.savez_compressed(existing,selected_ids=np.asarray(overlay.selected_ids,dtype=np.int32),
                            changed_ids=np.asarray(overlay.changed_ids,dtype=np.int32),
                            failed_ids=np.asarray(overlay.failed_ids,dtype=np.int32),
                            assigned_additions=np.empty((0,4),dtype=np.float32))
        repaired.append(Attempt(episode,event.cloud_id,"rearrangement",1.,"sustained",event.source_ns,
                                prior["base_sha256"],prior["seed_key"],target.cell_id,overlay.intended_count,
                                len(overlay.selected_ids),len(overlay.changed_ids),len(overlay.failed_ids),overlay.reason,
                                str(existing.relative_to(run)),file_sha256(existing),len(reread),file_sha256(path),
                                "accepted","VALID",len(reread),changed,0,float(distance.max()),
                                float(np.mean(cell_index(reread[:,:3],(0.,0.))>=0))))
        arm_events.append(replace(event,path=path))
    with (run/"clean_raw_cache.pkl").open("rb") as f: clean=pickle.load(f)
    arm_source=AllowedSource(clouds,poses,active)
    pose_rows={s:arm_source.read_poses(s) for s in ("003","004","laser")}
    attacked=replay(arm_events,arm_source,config=ReplayConfig(),poses=pose_rows)
    attacked_by={r.cloud_id:r for r in attacked}
    full=[attacked_by[r.cloud_id] if r.stream=="003" else r for r in clean]
    refs={}
    for row in load_rows(run/"T_R03_references.csv"):
        ref=ExploratoryReference(row["stream"],row["factor"],row["context"],
            float(row["q50"]) if row["q50"] else None,float(row["u"]) if row["u"] else None,
            float(row["b"]) if row["b"] else None,int(row["observations"]),row["segment"],row["status"],
            tuple(json.loads(row["row_ids"])),row["reference_id"])
        refs[(ref.stream,ref.factor,ref.context)]=ref
    scored,state=score_arm(full,refs,episode,1.,.5,first_ns)
    save_table(pred,episode+"_scores",scored)
    (pred/(episode+"_state.json")).write_text(json.dumps(state,indent=2)+"\n")
    by_id={r.cloud_id:r.as_dict() for r in repaired}
    replaced=[by_id[r["cloud_id"]] if r["episode"]==episode else r for r in old]
    save_table(run,"T_R03_attempts",replaced)
    flow["prediction_sha256"]=file_sha256(pred/(episode+"_scores.csv"))
    flow["checkpoint_sha256"]=file_sha256(pred/(episode+"_state.json"))
    flow["zero_realized"]=sum(r.realized_changed_rows==0 for r in repaired)
    save_table(run,"T_R03_episode_flow",flows)
    shutil.rmtree(active)
    seal={p.name:file_sha256(p) for p in pred.iterdir() if p.is_file()}
    (run/"prediction_seal.json").write_text(json.dumps(seal,indent=2)+"\n")
    intervals=json.loads((run/"evaluator_intervals.json").read_text())
    intervals["prediction_seal_sha256"]=file_sha256(run/"prediction_seal.json")
    (run/"evaluator_intervals.json").write_text(json.dumps(intervals,indent=2)+"\n")
    (run/"repair.log").write_text(f"Corrected same rearrangement episode {episode}: {len(repaired)} files reloaded through production reader; "
                                  "outside-D original rows remained unchanged; previous invalid prediction and ledgers retained.\n")
    print("repaired",episode,len(repaired),"files; failed selected moves",sum(x.failed_count for x in repaired))


if __name__=="__main__": main(Path(sys.argv[1]).resolve())
