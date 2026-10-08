"""Paired, evaluator-only oracle-minus-GT-free gap analysis for S04."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Mapping

import numpy as np

from valid_point.calibration import Calibration, calibrate
from valid_point.gt_free import GTFreeDecision, score_clouds
from valid_point.oracle import OracleBox, OracleDecision, decide_oracle
from valid_point.references import Reference, fit_references, select_reference
from valid_point.regions import FrozenTileGrid, make_fixed_grid


@dataclass(frozen=True)
class EvaluatorOutcome:
    """Post-decision truth used only to measure outcomes and form strata."""

    decision_id: str
    case: str
    attack: bool
    object_count: int | None
    expected_effect: str
    proposal_state: str
    association_state: str
    visibility_note: str


def _reference_rows(track: str, seeds: Iterable[int], frames_per_seed: int) -> list[dict]:
    patterns = {
        "gt_free": (0, 1, 2, 3, 4),
        "oracle_box": (0, 1, 1, 2),
    }
    pattern = patterns[track]
    rows = []
    for seed in seeds:
        for frame in range(frames_per_seed):
            rows.append({
                "split_role": "reference", "clean": True, "seed": seed,
                "segment": f"{track}_reference_{seed}", "frame": frame,
                "factor": "S", "region_id": f"{track}:broad",
                "value": pattern[(seed + frame) % len(pattern)], "units": "points",
                "sensor_class": "vehicle", "bin_id": f"{track}_count",
            })
    return rows


def fit_track_reference(track: str, config: Mapping) -> tuple[Reference, dict]:
    """Fit a track-local count reference; no fitted object-count stratum is shared."""
    seeds = tuple(config["splits"][track]["reference_seeds"])
    rows = _reference_rows(track, seeds, int(config["splits"][track]["frames_per_seed"]))
    bundle = fit_references(
        rows,
        min_rows=int(config["fitting"]["min_rows"]),
        min_segments=int(config["fitting"]["min_segments"]),
        allowed_seeds=set(seeds),
    )
    reference, mode = select_reference(bundle, "S", "vehicle", f"{track}_count")
    if reference is None:
        raise ValueError(f"{track} reference unavailable")
    return reference, {
        "track": track, "mode": mode, "context": reference.context,
        "n": reference.n, "segments": list(reference.segments), "q50": reference.q50,
        "u": reference.u, "b": reference.b, "units": reference.units,
        "reference_seeds": list(seeds),
    }


def fit_track_calibration(track: str, reference: Reference, config: Mapping) -> tuple[Calibration, dict]:
    """Calibrate only against that track's separately declared clean seeds."""
    seeds = tuple(config["splits"][track]["calibration_seeds"])
    frames_per_seed = int(config["splits"][track]["frames_per_seed"])
    rows = []
    index = 0
    for seed in seeds:
        for frame in range(frames_per_seed):
            # Four deterministic clean tails in 400 decisions. The fitted threshold
            # is retained even when it yields low power; no attack row tunes it.
            raw_max = reference.u + 1 if index % 100 == 99 else reference.u
            anomaly = max(0.0, min(1.0, (raw_max - reference.u) / reference.b))
            rows.append({
                "split_role": "calibration", "clean": True, "seed": seed,
                "segment": f"{track}_calibration_{seed}", "status": "known", "A": anomaly,
            })
            index += 1
    calibration = calibrate(
        rows, alpha=float(config["calibration"]["alpha"]),
        min_known=int(config["calibration"]["min_known"]), allowed_seeds=set(seeds),
    )
    return calibration, {
        **asdict(calibration), "track": track, "calibration_seeds": list(seeds),
        "reference_context": reference.context,
    }


def _points_in_box(lower: tuple[float, float, float], upper: tuple[float, float, float],
                   count: int) -> np.ndarray:
    if count == 0:
        return np.empty((0, 3), dtype=float)
    lo, hi = np.asarray(lower, dtype=float), np.asarray(upper, dtype=float)
    fraction = (np.arange(count, dtype=float) + .5) / count
    return lo + (hi - lo) * np.column_stack((fraction, fraction[::-1], np.full(count, .5)))


def _cloud(*groups: tuple[tuple[float, float, float], tuple[float, float, float], int]) -> np.ndarray:
    arrays = [_points_in_box(lower, upper, count) for lower, upper, count in groups]
    return np.concatenate(arrays) if arrays else np.empty((0, 3), dtype=float)


def spatial_case_fixtures(config: Mapping) -> tuple[tuple[dict, ...], dict[str, tuple[OracleBox, ...]], tuple[EvaluatorOutcome, ...]]:
    """Return operational clouds separately from evaluator boxes/outcomes."""
    deadline = int(config["decision"]["deadline_ns"])
    available = int(config["decision"]["available_ns"])
    a = ((.2, .2, -.5), (1.8, 1.8, .5), 2)
    b = ((2.2, .2, -.5), (3.8, 1.8, .5), 2)
    c5_left = ((9.5, 10.2, -.5), (10.0, 10.8, .5), 5)
    c5_right = ((10.0, 10.2, -.5), (10.5, 10.8, .5), 5)
    ghost8 = ((20.2, 20.2, -.5), (21.8, 21.8, .5), 8)
    outside8 = ((52.2, .2, -.5), (53.8, 1.8, .5), 8)
    unique8 = ((-19.8, 15.2, -.5), (-18.2, 16.8, .5), 8)
    changing7 = ((.2, .2, -.5), (1.8, 1.8, .5), 7)
    suspicious8 = ((.2, .2, -.5), (1.8, 1.8, .5), 8)
    rearranged_b4 = ((2.2, .2, -.5), (3.8, 1.8, .5), 4)
    ambiguous6 = ((1.5, .5, -.5), (2.5, 1.5, .5), 6)

    base = _cloud(a, b)
    specifications = (
        ("baseline", base, "present_nonempty", False, 2, "clean reference-like content", "none", "matched", "unknown"),
        ("in_box_addition", _cloud(a, b, suspicious8), "present_nonempty", True, 2, "concentrated positive addition", "none", "matched", "unknown"),
        ("missed_object_split_tiles", _cloud(a, b, c5_left, c5_right), "present_nonempty", True, 3, "oracle object spans two tiles", "missed", "matched", "unknown"),
        ("empty_region_ghost", _cloud(a, b, ghost8), "present_nonempty", True, 2, "ghost in receiver tile with no oracle box", "extra", "unmatched", "unknown"),
        ("unique_honest_view", _cloud(a, b, unique8), "present_nonempty", False, 3, "legitimate unique content", "extra", "matched", "unknown"),
        ("changing_content", _cloud(changing7, b), "present_nonempty", False, 2, "legitimate changing density", "split", "matched", "unknown"),
        ("merged_proposal", _cloud(a, b), "present_nonempty", False, 2, "two objects merged by optional proposal", "merged", "matched", "unknown"),
        ("association_ambiguity", _cloud(a, b, ambiguous6), "present_nonempty", True, 2, "overlapping association cannot identify source object", "merged", "ambiguous", "unknown"),
        ("outside_roi_addition", _cloud(a, b, outside8), "present_nonempty", True, 3, "positive addition outside operational ROI", "missed", "matched", "unknown"),
        ("count_preserving_rearrangement", _cloud(rearranged_b4), "present_nonempty", True, 2, "same tile count, redistributed between boxes", "split", "matched", "unknown"),
        ("present_empty", np.empty((0, 3)), "present_empty", False, 0, "zero returns; no visibility accusation", "missed", "unmatched", "unknown"),
        ("absent_cloud", None, "absent", True, None, "attempt unavailable by deadline", "unknown", "unknown", "unknown"),
    )
    operational = []
    outcomes = []
    boxes_by_id = {}
    box_a = OracleBox("oracle_box:A", a[0], a[1], "object:A")
    box_b = OracleBox("oracle_box:B", b[0], b[1], "object:B")
    box_c = OracleBox("oracle_box:C", (9.5, 10.2, -.5), (10.5, 10.8, .5), "object:C")
    box_u = OracleBox("oracle_box:U", unique8[0], unique8[1], "object:U")
    box_o = OracleBox("oracle_box:O", outside8[0], outside8[1], "object:O")
    for case, points, state, attack, objects, effect, proposal, association, visibility in specifications:
        decision_id = f"S04/sender_vehicle/frame_{len(operational):02d}/deadline_{deadline}"
        operational.append({
            "decision_id": decision_id, "deadline_ns": deadline,
            "available_ns": available if state.startswith("present") else None,
            "points_m": points, "message_state": state,
            "receiver_range_m": None, "kinematic_penalty": 0.0,
        })
        boxes = (box_a, box_b)
        if case == "missed_object_split_tiles": boxes += (box_c,)
        if case == "unique_honest_view": boxes += (box_u,)
        if case == "outside_roi_addition": boxes += (box_o,)
        boxes_by_id[decision_id] = boxes
        outcomes.append(EvaluatorOutcome(decision_id, case, attack, objects, effect,
                                         proposal, association, visibility))
    return tuple(operational), boxes_by_id, tuple(outcomes)


def compare_tracks(gt_free: tuple[GTFreeDecision, ...], oracle: tuple[OracleDecision, ...],
                   outcomes: tuple[EvaluatorOutcome, ...]) -> tuple[list[dict], dict]:
    """Join frozen decisions to evaluator outcomes and report both denominators."""
    gt_by_id = {row.measurement.decision_id: row for row in gt_free}
    oracle_by_id = {row.decision_id: row for row in oracle}
    if set(gt_by_id) != set(oracle_by_id) or set(gt_by_id) != {row.decision_id for row in outcomes}:
        raise ValueError("paired decision support mismatch")
    rows = []
    for truth in outcomes:
        gt = gt_by_id[truth.decision_id]
        ora = oracle_by_id[truth.decision_id]
        common = gt.score.status == ora.score.status == "known"
        gt_counts = tuple(gt.measurement.counts)
        oracle_counts = tuple(ora.counts)
        rows.append({
            "decision_id": truth.decision_id, "case": truth.case, "attack": truth.attack,
            "object_count_evaluator_only": truth.object_count,
            "expected_effect": truth.expected_effect, "proposal_state_deferred": truth.proposal_state,
            "association_state": truth.association_state, "visibility": truth.visibility_note,
            "gt_free_status": gt.score.status, "gt_free_T": gt.score.T,
            "gt_free_alarm": gt.alarm, "gt_free_outside_roi_points": gt.measurement.outside_roi_count,
            "gt_free_max_tile_count": max((value for _, value in gt_counts), default=None),
            "gt_free_nonempty_tiles": sum(value > 0 for _, value in gt_counts),
            "gt_free_context": gt.measurement.context_id,
            "raw_point_count": ((sum(value for _, value in gt_counts) + (gt.measurement.outside_roi_count or 0))
                                if gt.measurement.status == "known" else None),
            "oracle_status": ora.score.status, "oracle_T": ora.score.T,
            "oracle_alarm": ora.alarm, "common_support": common,
            "oracle_box_counts": ";".join(f"{name}={value}" for name, value in oracle_counts),
            "oracle_minus_gt_free_T": (ora.score.T - gt.score.T) if common else None,
            "gt_free_outcome": _outcome(gt.alarm, gt.score.status, truth.attack),
            "oracle_outcome": _outcome(ora.alarm, ora.score.status, truth.attack),
        })

    def metrics(track: str, subset: list[dict], denominator: str) -> dict:
        status = [row[f"{track}_status"] for row in subset]
        attacks = [row for row in subset if row["attack"]]
        benign = [row for row in subset if not row["attack"]]
        return {
            "denominator": denominator, "attempts": len(subset),
            "known": sum(value == "known" for value in status),
            "abstentions": sum(value != "known" for value in status),
            "attack_attempts": len(attacks),
            "attack_alarms": sum(row[f"{track}_alarm"] is True for row in attacks),
            "benign_attempts": len(benign),
            "false_alarms": sum(row[f"{track}_alarm"] is True for row in benign),
        }

    common_rows = [row for row in rows if row["common_support"]]
    summary = {
        "all_attempts": {
            "gt_free": metrics("gt_free", rows, "all attempted sender/frame/deadline decisions"),
            "oracle_box": metrics("oracle", rows, "all attempted sender/frame/deadline decisions"),
        },
        "common_support": {
            "gt_free": metrics("gt_free", common_rows, "both tracks known"),
            "oracle_box": metrics("oracle", common_rows, "both tracks known"),
            "paired_n": len(common_rows),
            "mean_oracle_minus_gt_free_T": (
                float(np.mean([row["oracle_minus_gt_free_T"] for row in common_rows])) if common_rows else None
            ),
        },
        "object_count_strata_evaluator_only": _object_strata(rows),
    }
    for support in ("all_attempts", "common_support"):
        gt = summary[support]["gt_free"]
        ora = summary[support]["oracle_box"]
        denominator = max(1, gt["attack_attempts"])
        summary[support]["oracle_minus_gt_free_attack_alarm_rate"] = (
            ora["attack_alarms"] - gt["attack_alarms"]
        ) / denominator
    return rows, summary


def _outcome(alarm_value: bool | None, status: str, attack: bool) -> str:
    if status != "known" or alarm_value is None:
        return "abstention"
    if attack:
        return "detected" if alarm_value else "missed"
    return "false_alarm" if alarm_value else "correct_non_alarm"


def _object_strata(rows: list[dict]) -> dict:
    output = {}
    for row in rows:
        key = "unknown" if row["object_count_evaluator_only"] is None else str(row["object_count_evaluator_only"])
        record = output.setdefault(key, {"attempts": 0, "gt_free_alarms": 0, "oracle_alarms": 0})
        record["attempts"] += 1
        record["gt_free_alarms"] += row["gt_free_alarm"] is True
        record["oracle_alarms"] += row["oracle_alarm"] is True
    return output


def run_spatial_experiment(config: Mapping) -> dict:
    """Execute the deterministic S04 study without file I/O."""
    geometry = config["gt_free_grid"]
    grid = make_fixed_grid(
        x_limits_m=tuple(geometry["x_limits_m"]), y_limits_m=tuple(geometry["y_limits_m"]),
        z_limits_m=tuple(geometry["z_limits_m"]), tile_size_m=tuple(geometry["tile_size_m"]),
        frozen_ns=int(geometry["frozen_ns"]), receiver_frame=str(geometry["receiver_frame"]),
    )
    gt_reference, gt_lineage = fit_track_reference("gt_free", config)
    oracle_reference, oracle_lineage = fit_track_reference("oracle_box", config)
    gt_calibration, gt_cal_lineage = fit_track_calibration("gt_free", gt_reference, config)
    oracle_calibration, oracle_cal_lineage = fit_track_calibration("oracle_box", oracle_reference, config)
    operational, boxes_by_id, outcomes = spatial_case_fixtures(config)
    gt_decisions = score_clouds(
        operational, grid=grid, reference=gt_reference, calibration=gt_calibration, config=config,
    )
    oracle_decisions = tuple(
        decide_oracle(
            decision_id=case["decision_id"], points_m=case["points_m"],
            boxes=boxes_by_id[case["decision_id"]], message_state=case["message_state"],
            reference=oracle_reference, kinematic_penalty=case["kinematic_penalty"],
            calibration=oracle_calibration,
            association_state=outcomes[index].association_state,
        )
        for index, case in enumerate(operational)
    )
    case_rows, gap = compare_tracks(gt_decisions, oracle_decisions, outcomes)
    blind = next(row for row in case_rows if row["case"] == "count_preserving_rearrangement")
    base = next(row for row in case_rows if row["case"] == "baseline")
    addition = next(row for row in case_rows if row["case"] == "in_box_addition")
    return {
        "grid": {
            "tile_count": len(grid.tiles), "digest": grid.digest,
            "empty_tiles_baseline": sum(value == 0 for _, value in gt_decisions[0].measurement.counts),
            "units": "m and points", "frozen_ns": grid.frozen_ns,
        },
        "decision": dict(config["decision"]),
        "references": {"gt_free": gt_lineage, "oracle_box": oracle_lineage},
        "calibrations": {"gt_free": gt_cal_lineage, "oracle_box": oracle_cal_lineage},
        "cases": case_rows, "gap": gap,
        "contract_checks": {
            "count_preserving_gt_free_unchanged": blind["gt_free_T"] == base["gt_free_T"],
            "added_points_do_not_improve_T": addition["gt_free_T"] <= base["gt_free_T"],
            "outside_roi_points_visible": next(row for row in case_rows if row["case"] == "outside_roi_addition")["gt_free_outside_roi_points"] == 8,
            "present_empty_not_accused": next(row for row in case_rows if row["case"] == "present_empty")["gt_free_alarm"] is False,
            "absent_abstains": next(row for row in case_rows if row["case"] == "absent_cloud")["gt_free_status"] == "unknown",
        },
        "gate": {
            "technical": "PASS",
            "G3": "FAIL_NEGATIVE_RESULT",
            "operational_readiness": "BLOCKED",
            "reason": "Constructed evidence exposes misses, false alarms, an outside-ROI miss, count-preserving blindness, and abstention; illustrative fixtures cannot establish operational defensibility.",
        },
    }
