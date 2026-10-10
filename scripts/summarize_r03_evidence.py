"""Offline paired summaries after R03 prediction sealing; never feeds scoring."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import pickle
import sys

import numpy as np

from valid_point.attacks.overlays import apply_overlay
from valid_point.io.mixed_signals import read_pcd

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay_development import save_table


def rows(path):
    with path.open(newline="") as f: return list(csv.DictReader(f))


def save(path, data):
    columns=list(dict.fromkeys(k for row in data for k in row))
    with path.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns); writer.writeheader(); writer.writerows(data)
    with path.with_suffix(".md").open("w") as f:
        f.write(f"# {path.stem}\n\n{len(data)} rows. Values are development-only. Full rows: [{path.name}]({path.name}).\n\n")
        f.write("| "+" | ".join(columns)+" |\n| "+" | ".join("---" for _ in columns)+" |\n")
        for row in data:
            f.write("| "+" | ".join(str(row.get(k,"")) for k in columns)+" |\n")


def number(value):
    try: return float(value)
    except (TypeError,ValueError): return None


def main(run: Path):
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((run/"config.json").read_text())
    base=root/"data/mixed_signals"/cfg["revision"]/"raw/PointClouds/mini_7"
    attempts=rows(run/"T_R03_attempts.csv")
    with (run/"clean_raw_cache.pkl").open("rb") as f:
        clean_raw=pickle.load(f)
    save_table(run,"T_R03_clean_raw_records",[record.as_dict() for record in clean_raw])
    movement=[]
    for row in attempts:
        if row["family"] not in ("displacement","rearrangement"):
            continue
        with (base/row["cloud_id"]).open("rb") as f: _, values=read_pcd(f)
        generated=apply_overlay(values,family=row["family"],severity=float(row["severity"]),key=row["seed_key"])
        selected=np.asarray(generated.selected_ids,dtype=int)
        changed=np.asarray(generated.changed_ids,dtype=int)
        lengths=np.linalg.norm(generated.values[changed,:3]-values[changed,:3],axis=1) if len(changed) else np.empty(0)
        reread_max=number(row["realized_max_displacement_m"])
        maximum=float(lengths.max()) if len(lengths) else 0.
        movement.append({"episode":row["episode"],"cloud_id":row["cloud_id"],
                         "family":row["family"],"intended_offset_m":row["severity"],
                         "selected_rows":len(selected),"moved_rows":len(changed),
                         "failed_rows":len(generated.failed_ids),
                         "moved_fraction_of_selected":len(changed)/len(selected) if len(selected) else None,
                         "norm_p50_m":float(np.quantile(lengths,.5)) if len(lengths) else None,
                         "norm_p90_m":float(np.quantile(lengths,.9)) if len(lengths) else None,
                         "norm_max_m":maximum,"reader_max_m":reread_max,
                         "regenerated_vs_reader_max_abs_m":abs(maximum-reread_max) if reread_max is not None else None,
                         "reader_status":row["reader_status"]})
    save(run/"T_R03_movement.csv",movement)
    clean=rows(run/"sealed_predictions/clean_scores.csv")
    clean_map={(r["cloud_id"],r["arm"]):r for r in clean}
    paired=[]
    for flow in rows(run/"T_R03_episode_flow.csv"):
        episode=flow["episode"]
        attacked=rows(run/"sealed_predictions"/(episode+"_scores.csv"))
        for stream in ("003","004","laser","top","dome"):
            for arm in ("D-only","G-only","max(D,G)"):
                sample=[r for r in attacked if r["stream"]==stream and r["arm"]==arm]
                effects=[]; temporal=[]; equal_companion=True
                for r in sample:
                    c=clean_map[(r["cloud_id"],arm)]
                    a1,a0=number(r["C"]),number(c["C"])
                    z1,z0=number(r["C_time"]),number(c["C_time"])
                    if a1 is not None and a0 is not None: effects.append(a1-a0)
                    if r["state_ready"]=="True" and c["state_ready"]=="True" and z1 is not None and z0 is not None:
                        temporal.append(z1-z0)
                    if stream!="003" and (r["C"],r["Z"],r["A"])!=(c["C"],c["Z"],c["A"]): equal_companion=False
                paired.append({"episode":episode,"family":flow["family"],"schedule":flow["schedule"],
                               "stream":stream,"arm":arm,"attempted":len(sample),
                               "memoryless_paired_known":len(effects),"mean_attacked_minus_clean_C":float(np.mean(effects)) if effects else None,
                               "temporal_postwarm_paired_known":len(temporal),
                               "mean_attacked_minus_clean_C_time":float(np.mean(temporal)) if temporal else None,
                               "honest_companion_scores_identical":equal_companion if stream!="003" else None})
    save(run/"T_R03_paired_effects.csv",paired)
    clean_g={r["cloud_id"]:r for r in clean if r["stream"]=="003" and r["arm"]=="D-only"}
    history=[]
    for flow in rows(run/"T_R03_episode_flow.csv"):
        episode=flow["episode"]
        windows=cfg["schedules_s"][flow["schedule"]]
        onset=min(start for start,_ in windows); offset=max(end for _,end in windows)
        attacked=[r for r in rows(run/"sealed_predictions"/(episode+"_scores.csv")) if r["stream"]=="003" and r["arm"]=="D-only"]
        groups={name:[] for name in ("pre","during","between_bursts","post_first_1s","post_later")}
        for r in attacked:
            t=float(r["elapsed_s"])
            name=("pre" if t<onset else "during" if any(start<=t<end for start,end in windows)
                  else "between_bursts" if t<offset else "post_first_1s" if t<offset+1 else "post_later")
            groups[name].append(r)
        for phase,sample in groups.items():
            if not sample: continue
            differences=[]; mismatched_known=0
            for r in sample:
                baseline=clean_g[r["cloud_id"]]
                one,zero=number(r["raw_G_m"]),number(baseline["raw_G_m"])
                if one is not None and zero is not None: differences.append(one-zero)
                if (one is None)!=(zero is None): mismatched_known+=1
            history.append({"episode":episode,"family":flow["family"],"schedule":flow["schedule"],
                            "phase":phase,"attempted_events":len(sample),"paired_known_G":len(differences),
                            "knownness_mismatch":mismatched_known,
                            "mean_attacked_minus_clean_G_m":float(np.mean(differences)) if differences else None,
                            "mean_abs_paired_G_difference_m":float(np.mean(np.abs(differences))) if differences else None,
                            "interpretation":"attacked-arm prior geometry; no clean shadow or forced recovery"})
    save(run/"T_R03_history.csv",history)
    # Export the raw values actually carried in each scored arm with input-byte
    # lineage. This join is post-seal and is never supplied back to the scorer.
    base_hash={r.cloud_id:r.input_sha256 for r in clean_raw}
    clean_by_id={r.cloud_id:r for r in clean_raw}
    derived_hash={(r["episode"],r["cloud_id"]):r["derived_sha256"] for r in attempts}
    observations=[]
    for flow in rows(run/"T_R03_episode_flow.csv"):
        for row in rows(run/"sealed_predictions"/(flow["episode"]+"_scores.csv")):
            if row["arm"]!="D-only": continue
            clean_record=clean_by_id[row["cloud_id"]]
            point_only=flow["family"]!="calibration_timing"
            observations.append({"episode":flow["episode"],"cloud_id":row["cloud_id"],
                                 "stream":row["stream"],"principal":row["principal"],
                                 "source_ns":row["source_ns"],"elapsed_s":row["elapsed_s"],
                                 "input_sha256":derived_hash.get((flow["episode"],row["cloud_id"]),base_hash[row["cloud_id"]]),
                                 "pose_id":clean_record.pose_id if point_only else None,
                                 "pose_id_reason":"same metadata as clean" if point_only else "IN_MEMORY_ADAPTER_CONTROL_NOT_EXPORTED",
                                 "history_id":clean_record.history_id if point_only else None,
                                 "history_id_reason":"same event sequence" if point_only else "IN_MEMORY_ADAPTER_CONTROL_NOT_EXPORTED",
                                 "raw_D_counts":row["raw_D_counts"],"raw_D_inside_points":row["raw_D_inside_points"],
                                 "raw_G_m":row["raw_G_m"],"raw_G_reason":row["raw_G_reason"],
                                 "pose_age_s":row["pose_age_s"],"G_gap_s":row["G_gap_s"],
                                 "units":"D points/cell/frame; G m; time s"})
    save(run/"T_R03_raw_observations.csv",observations)
    print("movement rows",len(movement),"paired summary rows",len(paired))


if __name__=="__main__": main(Path(sys.argv[1]).resolve())
