"""Export distinct R03 operational record views from sealed decision rows."""
from __future__ import annotations

import csv
from pathlib import Path
import pickle
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay_development import save_table


def rows(path):
    with path.open(newline="") as f: return list(csv.DictReader(f))


def main(run: Path):
    with (run/"clean_raw_cache.pkl").open("rb") as f: clean=pickle.load(f)
    hashes={("clean",r.cloud_id):r.input_sha256 for r in clean}
    for row in rows(run/"T_R03_raw_observations.csv"):
        hashes[(row["episode"],row["cloud_id"])]=row["input_sha256"]
    flows=rows(run/"T_R03_episode_flow.csv")
    episodes=["clean"]+[r["episode"] for r in flows]
    normalized=[]; instant=[]; temporal=[]; alarms=[]
    for episode in episodes:
        path=run/"sealed_predictions"/("clean_scores.csv" if episode=="clean" else episode+"_scores.csv")
        for row in rows(path):
            common={"episode":episode,"cloud_id":row["cloud_id"],"stream":row["stream"],
                    "principal":row["principal"],"source_ns":row["source_ns"],
                    "elapsed_s":row["elapsed_s"],"arm":row["arm"],
                    "input_sha256":hashes[(episode,row["cloud_id"])]}
            if row["arm"]=="D-only":
                normalized.append({**{k:v for k,v in common.items() if k!="arm"},
                    "D":row["D_anomaly"],"G":row["G_anomaly"],
                    "D_status":"known" if row["D_anomaly"]!="" else "unknown",
                    "G_status":"known" if row["G_anomaly"]!="" else "unknown",
                    "D_reason":row["D_reason"],"G_reason":row["G_reason"],
                    "D_contexts":row["D_contexts"],"G_context":row["G_context"],
                    "reference_id":"R03.exploratory.mini_7.v1","units":"unitless clipped anomaly; raw D points/cell, raw G m"})
            instant.append({**common,"status":row["score_status"],"reason":row["score_reason"],
                            "A":row["A"],"C":row["C"],"reference_id":"R03.exploratory.mini_7.v1"})
            temporal.append({**common,"status":row["state_status"],"reason":row["state_reason"],
                             "Z":row["Z"],"C_time":row["C_time"],"held_Z":row["held_Z"],
                             "held_age_s":row["held_age_s"],"eligible_updates":row["state_updates"],
                             "contiguous_s":row["contiguous_s"],"ready":row["state_ready"],
                             "reset":row["state_reset"],"reference_id":"R03.exploratory.mini_7.v1"})
            alarms.append({**common,"status":"unknown","instant_alarm":row["instant_alarm"],
                           "temporal_alarm":row["temporal_alarm"],"threshold_id":row["threshold_id"],
                           "reason":row["alarm_reason"],"reference_id":"R03.exploratory.mini_7.v1"})
    if len(normalized)!=len(episodes)*1250 or any(len(x)!=len(episodes)*1250*3 for x in (instant,temporal,alarms)):
        raise RuntimeError("distinct R03 record cardinality mismatch")
    if any(x["instant_alarm"] or x["temporal_alarm"] or x["threshold_id"] for x in alarms):
        raise RuntimeError("uncalibrated alarm acquired a value")
    save_table(run,"T_R03_normalized_factors",normalized)
    save_table(run,"T_R03_instantaneous_decisions",instant)
    save_table(run,"T_R03_temporal_states",temporal)
    save_table(run,"T_R03_alarm_decisions",alarms)
    print("distinct records",len(normalized),len(instant),len(temporal),len(alarms))


if __name__=="__main__": main(Path(sys.argv[1]).resolve())
