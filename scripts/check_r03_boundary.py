"""Exercise changed/withheld evaluator files against real mini_7 score/state."""
from __future__ import annotations

import csv
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys

from valid_point.development_scores import ExploratoryReference, decide, normalize_raw
from valid_point.replay import AllowedSource, ReplayConfig, replay
from valid_point.temporal import TemporalEWMA


def evaluate(events, clouds, poses, refs):
    source=AllowedSource(clouds,poses)
    raw=replay(events,source,config=ReplayConfig(),
               poses={s:source.read_poses(s) for s in ("003","004","laser")})
    state=TemporalEWMA(1.,.5)
    decisions=[]
    for row in raw:
        factors=normalize_raw(row,refs,"R03.exploratory.mini_7.v1")
        for arm in ("D-only","G-only","max(D,G)"):
            score=decide(row,factors,arm)
            temporal=state.update(episode="boundary",principal=row.principal,sensor=row.stream,
                                  method_arm=arm,reference_version=score.reference_id,
                                  source_ns=row.source_ns,A=score.A,reason=score.reason)
            decisions.append((score.as_dict(),temporal.as_dict()))
    return decisions,state.checkpoint(),source.access_log


def main(run: Path):
    root=Path(__file__).resolve().parents[1]
    config=json.loads((run/"config.json").read_text())
    rawroot=root/"data/mixed_signals"/config["revision"]/"raw"
    clouds=rawroot/"PointClouds/mini_7"; poses=rawroot/"Odometry/mini_7"
    source=AllowedSource(clouds,poses)
    events=source.events(max_sync_id=11,first_seconds=1.2)
    refs={}
    with (run/"T_R03_references.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            ref=ExploratoryReference(row["stream"],row["factor"],row["context"],
                                      float(row["q50"]) if row["q50"] else None,
                                      float(row["u"]) if row["u"] else None,
                                      float(row["b"]) if row["b"] else None,
                                      int(row["observations"]),row["segment"],row["status"],
                                      tuple(json.loads(row["row_ids"])),row["reference_id"])
            refs[(ref.stream,ref.factor,ref.context)]=ref
    eval_dir=run/"evaluator_boundary"; eval_dir.mkdir(exist_ok=False)
    filenames=("labels.json","boxes.json","attack_schedule.json","masks.json","clean_counterpart.json","outcomes.json")
    for name in filenames: (eval_dir/name).write_text('{"changed":false}\n')
    baseline=evaluate(events,clouds,poses,refs)
    for name in filenames: (eval_dir/name).write_text('{"changed":true,"value":999}\n')
    changed=evaluate(events,clouds,poses,refs)
    for name in filenames: (eval_dir/name).unlink()
    withheld=evaluate(events,clouds,poses,refs)
    probe=eval_dir/"forbidden.pcd"; probe.write_text("forbidden\n")
    trapped=False
    try: source._check(probe,source.clouds_dir)
    except PermissionError: trapped=True
    # A deliberately leaky reader must differ on changed evaluator content.
    positive_before=probe.read_text(); probe.write_text("changed\n"); positive_after=probe.read_text()
    result={"real_mini_7_events":len(events),"decision_count":len(baseline[0]),
            "changed_evaluator_identical_scores_and_complete_state":baseline[:2]==changed[:2],
            "withheld_evaluator_identical_scores_and_complete_state":baseline[:2]==withheld[:2],
            "access_logs_identical":baseline[2]==changed[2]==withheld[2],
            "evaluator_accesses":sum(str(eval_dir) in path for path in baseline[2]),
            "positive_control_trapped":trapped and positive_before!=positive_after,
            "decision_state_sha256":sha256(json.dumps(baseline[:2],sort_keys=True).encode()).hexdigest(),
            "input_sha256":{e.cloud_id:sha256(e.path.read_bytes()).hexdigest() for e in events}}
    (run/"boundary_isolation.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="input_sha256"},indent=2))
    if not all((result[k] for k in ("changed_evaluator_identical_scores_and_complete_state",
                                    "withheld_evaluator_identical_scores_and_complete_state",
                                    "access_logs_identical","positive_control_trapped"))) or result["evaluator_accesses"]:
        raise RuntimeError("R03 score/state evaluator boundary failed")


if __name__=="__main__": main(Path(sys.argv[1]).resolve())
