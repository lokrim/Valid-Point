"""Post-seal technical and provenance audit for a single R03 run."""
from __future__ import annotations

import csv
from hashlib import sha256
import json
from pathlib import Path
import pickle
import sys
import xml.etree.ElementTree as ET

import numpy as np

from valid_point.attacks.manifests import file_sha256

sys.path.insert(0,str(Path(__file__).resolve().parent))
from replay_development import save_table


def table(path):
    with path.open(newline="") as f: return list(csv.DictReader(f))


def check(condition, message, failures):
    if not condition: failures.append(message)


def main(run: Path):
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((run/"config.json").read_text())
    manifest=json.loads((run/"manifest.json").read_text())
    failures=[]
    with (run/"clean_raw_cache.pkl").open("rb") as f: clean=pickle.load(f)
    clean_by_id={r.cloud_id:r for r in clean}
    first_ns=min(r.source_ns for r in clean)
    check(len(clean)==1250,"clean event count",failures)
    check(set(r.stream for r in clean)=={"003","004","laser","top","dome"},"five streams",failures)
    rawroot=root/"data/mixed_signals"/cfg["revision"]/"raw/PointClouds/mini_7"
    base_match=all(file_sha256(rawroot/cloud_id)==digest for cloud_id,digest in manifest["input_sha256"].items())
    check(base_match,"base hashes changed",failures)
    references=table(run/"T_R03_references.csv")
    supported=[r for r in references if r["status"]=="supported_exploratory"]
    check(all(r["segment"]=="mini_7" and len(set(json.loads(r["row_ids"])))>=50 for r in supported),
          "exploratory distinct-cloud support",failures)
    calibration=table(run/"T_R03_calibration.csv")
    check(all(int(r["instant_known"])<200 and int(r["temporal_ready_known"])<200 and
              r["instant_threshold"]=="" and r["temporal_threshold"]=="" for r in calibration),
          "diagnostic calibration availability",failures)
    roundtrip=table(run/"T_R03_roundtrip.csv")
    check(len(roundtrip)==5 and all(float(r["max_abs_field_error"])<=1e-6 for r in roundtrip),
          "five identity controls",failures)
    zero=[{"family":r["family"],"cloud_id":r["cloud_id"],"base_sha256":r["base_sha256"],
           "writer_reloader_sha256":r["derived_sha256"],"max_abs_field_error":r["max_abs_field_error"],
           "clean_replay_reused":"yes; pointwise zero overlay identity verified by unit test and real PCD round trip"}
          for r in roundtrip]
    save_table(run,"T_R03_zero_controls",zero)
    attempts=table(run/"T_R03_attempts.csv")
    selection_match=True; rearrangement_valid=True; reader_accepted=True
    for row in attempts:
        ledger=run/row["selection_ledger"]
        if file_sha256(ledger)!=row["selection_ledger_sha256"]: selection_match=False
        with np.load(ledger) as ids:
            if len(ids["selected_ids"])!=int(row["selected_count"]) or len(ids["failed_ids"])!=int(row["failed_count"]):
                selection_match=False
        if row["reader_status"]!="accepted" or not row["derived_sha256"]: reader_accepted=False
        if row["family"]=="rearrangement" and (int(row["realized_cell_changes"])!=0 or
              int(row["selected_count"])!=int(row["injected_changed_count"])+int(row["failed_count"])):
            rearrangement_valid=False
    check(selection_match,"selection ledger hashes/counts",failures)
    check(reader_accepted,"derived production reader acceptance",failures)
    check(rearrangement_valid,"corrected rearrangement cell preservation/failures",failures)
    flows=table(run/"T_R03_episode_flow.csv")
    check(len(flows)==8 and len(attempts)==641,"bounded episode/attempt grid",failures)
    pred_dir=run/"sealed_predictions"
    seal=json.loads((run/"prediction_seal.json").read_text())
    check(all(file_sha256(pred_dir/name)==digest for name,digest in seal.items()),"prediction seal",failures)
    evaluator=json.loads((run/"evaluator_intervals.json").read_text())
    check(evaluator["prediction_seal_sha256"]==file_sha256(run/"prediction_seal.json"),
          "evaluator join after prediction seal",failures)
    clean_scores=table(pred_dir/"clean_scores.csv")
    clean_score_map={(r["cloud_id"],r["arm"]):r for r in clean_scores}
    prefix_equal=True; null_alarms=True; strict_unknown=True; time_axis=True; companion_equal=True
    clean_work_exhaustions=sum(r.geometry.reason=="NEIGHBOR_WORK_BUDGET" for r in clean)
    for flow in flows:
        scored=table(pred_dir/(flow["episode"]+"_scores.csv"))
        if len(scored)!=len(clean)*3: failures.append("missing scored event rows: "+flow["episode"])
        for row in scored:
            baseline=clean_score_map[(row["cloud_id"],row["arm"])]
            if row["instant_alarm"] or row["temporal_alarm"] or row["threshold_id"]: null_alarms=False
            if (row["score_status"]=="unknown")!=(row["A"]=="" and row["C"]==""): strict_unknown=False
            if row["state_status"]=="unknown" and (row["Z"] or row["C_time"]): strict_unknown=False
            if abs(float(row["elapsed_s"])-(int(row["source_ns"])-first_ns)/1e9)>1e-8: time_axis=False
            values=("A","C","Z","C_time","state_reason","state_updates","state_ready")
            if row["stream"]!="003" and any(row[k]!=baseline[k] for k in values): companion_equal=False
            if flow["family"] in ("random_removal","localized_removal","displacement","rearrangement","addition") and float(row["elapsed_s"])<5:
                if any(row[k]!=baseline[k] for k in values): prefix_equal=False
    check(null_alarms,"uncalibrated alarms must be null",failures)
    check(strict_unknown,"strict score/state unknowns",failures)
    check(time_axis,"source-ns elapsed axes",failures)
    check(companion_equal,"honest companion score/state equality",failures)
    check(prefix_equal,"actual malicious-arm prefix invariance",failures)
    normalized_records=table(run/"T_R03_normalized_factors.csv")
    instant_records=table(run/"T_R03_instantaneous_decisions.csv")
    temporal_records=table(run/"T_R03_temporal_states.csv")
    alarm_records=table(run/"T_R03_alarm_decisions.csv")
    check(len(normalized_records)==9*1250 and len(instant_records)==9*1250*3 and
          len(temporal_records)==len(instant_records) and len(alarm_records)==len(instant_records),
          "distinct record ledger cardinality",failures)
    check(all(r["status"]=="unknown" and not r["instant_alarm"] and not r["temporal_alarm"] and
              not r["threshold_id"] for r in alarm_records),"distinct null alarm ledger",failures)
    boundary=json.loads((run/"boundary_isolation.json").read_text())
    check(all(boundary[k] for k in ("changed_evaluator_identical_scores_and_complete_state",
                                     "withheld_evaluator_identical_scores_and_complete_state",
                                     "access_logs_identical","positive_control_trapped")) and boundary["evaluator_accesses"]==0,
          "real mini_7 evaluator isolation",failures)
    xml=ET.parse(run/"test_results_full.xml").getroot()
    suite=xml if xml.tag=="testsuite" else xml.find("testsuite")
    tests=int(suite.attrib["tests"]); failures_in_tests=int(suite.attrib.get("failures",0))+int(suite.attrib.get("errors",0))
    check(tests>=100 and failures_in_tests==0,"full regression suite",failures)
    import nbformat
    nb=nbformat.read(run/"R03_replay_temporal.executed.ipynb",as_version=4)
    executed=sum(c.cell_type=="code" and c.execution_count is not None for c in nb.cells)
    errors=sum(out.output_type=="error" for c in nb.cells if c.cell_type=="code" for out in c.outputs)
    check(executed==5 and errors==0,"fresh executed notebook",failures)
    required=[run/(f"F_R03_{name}.{ext}") for name in ("geometry","timelines") for ext in ("png","svg","pdf")]
    check(all(p.exists() and p.stat().st_size>0 for p in required),"figure exports",failures)
    timestamps={stream:sorted(r.source_ns for r in clean if r.stream==stream) for stream in ("003","004","laser","top","dome")}
    cadence={stream:{"median_s":float(np.median(np.diff(values)/1e9)),
                      "p95_s":float(np.quantile(np.diff(values)/1e9,.95)),
                      "max_s":float(np.max(np.diff(values)/1e9))} for stream,values in timestamps.items()}
    tau=json.loads((run/"tau_choice.json").read_text())
    tau["clean_source_cadence_by_stream_s"]=cadence
    tau["g_reset_basis"]="0.5 s exceeds ordinary clean cadence and matches the frozen R02 maximum G gap; held unknowns do not decay"
    (run/"tau_choice.json").write_text(json.dumps(tau,indent=2)+"\n")
    report={"technical_pass":not failures,"failures":failures,"clean_events":len(clean),
            "executed_episodes":len(flows),"accepted_derived_attempts":sum(r["reader_status"]=="accepted" for r in attempts),
            "failed_rearrangement_moves":sum(int(r["failed_count"]) for r in attempts if r["family"]=="rearrangement"),
            "clean_G_work_budget_unknowns":clean_work_exhaustions,"identity_controls":len(roundtrip),
            "base_hashes_identical":base_match,"selection_ledgers_verified":selection_match,
            "all_companion_scores_and_state_identical":companion_equal,"malicious_prefix_invariant":prefix_equal,
            "null_alarms":null_alarms,"calibration_unavailable":True,"boundary":boundary,
            "full_tests":tests,"notebook_executed_code_cells":executed,"figure_exports":len(required),
            "reference_supported_contexts":len(supported),"reference_total_contexts":len(references),
            "normalized_factor_records":len(normalized_records),
            "instantaneous_records":len(instant_records),"temporal_records":len(temporal_records),
            "alarm_records":len(alarm_records)}
    (run/"validation.json").write_text(json.dumps(report,indent=2)+"\n")
    save_table(run,"T_R03_validation",[{"check":k,"value":v} for k,v in report.items() if k!="boundary" and k!="failures"])
    print(json.dumps({k:v for k,v in report.items() if k not in ("boundary",)},indent=2))
    if failures: raise RuntimeError("R03 technical validation failed")


if __name__=="__main__": main(Path(sys.argv[1]).resolve())
