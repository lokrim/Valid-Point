"""Evaluator-only oracle-box research track; never an operational scorer input."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from .calibration import Calibration, alarm
from .references import Reference, normalize
from .scoring import Score, score


@dataclass(frozen=True)
class OracleBox:
    region_id: str
    lower_m: tuple[float, float, float]
    upper_m: tuple[float, float, float]
    evaluator_object_id: str

    def __post_init__(self) -> None:
        lower, upper = np.asarray(self.lower_m), np.asarray(self.upper_m)
        if (not self.region_id.startswith("oracle_box:") or not self.evaluator_object_id
                or lower.shape != (3,) or upper.shape != (3,)
                or not np.isfinite((lower, upper)).all() or not (upper > lower).all()):
            raise ValueError("invalid evaluator oracle box")


@dataclass(frozen=True)
class OracleDecision:
    decision_id: str
    status: str
    counts: tuple[tuple[str, int], ...]
    spatial_penalty: float | None
    score: Score
    alarm: bool | None
    association_state: str
    track: str = "oracle_box"

    def as_dict(self) -> dict:
        row = asdict(self)
        row["T"] = self.score.T
        row["score_status"] = self.score.status
        row["A"] = self.score.A_observed if self.score.status == "known" else None
        return row


def decide_oracle(*, decision_id: str, points_m: np.ndarray | None,
                  boxes: tuple[OracleBox, ...], message_state: str,
                  reference: Reference | None, kinematic_penalty: float | None,
                  calibration: Calibration | None, association_state: str = "matched") -> OracleDecision:
    """Score fixed evaluator boxes for descriptive paired research only."""
    if message_state not in {"present_nonempty", "present_empty"} or points_m is None:
        result = score("vehicle", kinematic_penalty, None, reasons=("CLOUD_UNAVAILABLE",))
        return OracleDecision(decision_id, "unknown", (), None, result, None, association_state)
    if not boxes or reference is None:
        result = score("vehicle", kinematic_penalty, None, reasons=("NO_ORACLE_BOX",))
        return OracleDecision(decision_id, "unknown", (), None, result, None, association_state)
    points = np.asarray(points_m, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError("oracle points must be finite N x 3")
    counts = []
    penalties = []
    for box in boxes:
        inside = ((points >= box.lower_m) & (points < box.upper_m)).all(axis=1)
        count = int(inside.sum())
        counts.append((box.region_id, count))
        penalties.append((normalize(float(count), reference), box.region_id))
    spatial, strongest = max(penalties, key=lambda item: item[0])
    result = score("vehicle", kinematic_penalty, spatial, region=strongest)
    alarm_value = alarm(result.A_observed, calibration) if calibration is not None and result.status == "known" else None
    return OracleDecision(decision_id, "known", tuple(counts), spatial, result, alarm_value, association_state)
