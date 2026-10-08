import inspect
import json
from pathlib import Path

import numpy as np

from valid_point.evaluation.gap import (
    fit_track_calibration,
    fit_track_reference,
    run_spatial_experiment,
    spatial_case_fixtures,
)
from valid_point.gt_free import score_clouds
from valid_point.regions import make_fixed_grid


ROOT = Path(__file__).resolve().parents[1]


def _config():
    return json.loads((ROOT / "configs/spatial_tracks.json").read_text())


def _operational_scores():
    config = _config()
    geometry = config["gt_free_grid"]
    grid = make_fixed_grid(
        x_limits_m=tuple(geometry["x_limits_m"]), y_limits_m=tuple(geometry["y_limits_m"]),
        z_limits_m=tuple(geometry["z_limits_m"]), tile_size_m=tuple(geometry["tile_size_m"]),
        frozen_ns=geometry["frozen_ns"], receiver_frame=geometry["receiver_frame"],
    )
    reference, _ = fit_track_reference("gt_free", config)
    calibration, _ = fit_track_calibration("gt_free", reference, config)
    cases, _, labels = spatial_case_fixtures(config)
    decisions = score_clouds(cases, grid=grid, reference=reference, calibration=calibration, config=config)
    compact = tuple((row.measurement.decision_id, row.score.status, row.score.T, row.alarm,
                     row.measurement.region_digest) for row in decisions)
    return compact, labels


def test_withholding_and_permuting_evaluator_labels_leaves_gt_free_scores_identical():
    scores, labels = _operational_scores()
    withheld = None
    permuted = tuple(reversed(labels))
    scores_again, _ = _operational_scores()
    assert withheld is None and permuted != labels
    assert scores_again == scores


def test_operational_api_cannot_accept_gt_or_evaluator_labels():
    parameters = set(inspect.signature(score_clouds).parameters)
    forbidden = {"labels", "gt", "gt_boxes", "attack_mask", "clean_counterpart", "object_count"}
    assert parameters.isdisjoint(forbidden)


def test_added_suspicious_points_cannot_improve_T_at_fixed_context():
    config = _config()
    geometry = config["gt_free_grid"]
    grid = make_fixed_grid(
        x_limits_m=tuple(geometry["x_limits_m"]), y_limits_m=tuple(geometry["y_limits_m"]),
        z_limits_m=tuple(geometry["z_limits_m"]), tile_size_m=tuple(geometry["tile_size_m"]),
        frozen_ns=0,
    )
    reference, _ = fit_track_reference("gt_free", config)
    calibration, _ = fit_track_calibration("gt_free", reference, config)
    base = np.array([[.1 + .1*i, .1, 0.0] for i in range(4)])
    scores = []
    for added in range(9):
        points = np.vstack((base, np.array([[1.0 + .01*i, 1.0, 0.0] for i in range(added)]))) if added else base
        case = ({
            "decision_id": f"sweep:{added}", "deadline_ns": 10, "available_ns": 5,
            "points_m": points, "message_state": "present_nonempty",
            "receiver_range_m": None, "kinematic_penalty": 0.0,
        },)
        scores.append(score_clouds(case, grid=grid, reference=reference,
                                   calibration=calibration, config=config)[0].score.T)
    assert all(left >= right for left, right in zip(scores, scores[1:]))


def test_count_preserving_blind_spot_and_required_gap_inventory_are_visible():
    result = run_spatial_experiment(_config())
    rows = {row["case"]: row for row in result["cases"]}
    assert rows["count_preserving_rearrangement"]["gt_free_T"] == rows["baseline"]["gt_free_T"]
    assert rows["count_preserving_rearrangement"]["oracle_alarm"] is True
    assert rows["present_empty"]["gt_free_alarm"] is False
    assert rows["absent_cloud"]["gt_free_outcome"] == "abstention"
    assert rows["outside_roi_addition"]["gt_free_outside_roi_points"] == 8
    assert {row["proposal_state_deferred"] for row in result["cases"]} >= {"missed", "extra", "merged", "split"}
    assert any(row["association_state"] == "ambiguous" for row in result["cases"])
    assert result["references"]["gt_free"]["reference_seeds"] != result["references"]["oracle_box"]["reference_seeds"]
    assert result["calibrations"]["gt_free"]["calibration_seeds"] != result["calibrations"]["oracle_box"]["calibration_seeds"]
    assert result["gate"]["G3"] == "FAIL_NEGATIVE_RESULT"
