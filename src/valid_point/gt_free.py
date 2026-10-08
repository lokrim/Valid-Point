"""Operational GT-free spatial measurement and scoring.

This module intentionally has no evaluator-label, GT-box, attack-mask, or
clean-counterpart input.  It is safe to import without the oracle namespace.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping

import numpy as np

from .calibration import Calibration, alarm
from .references import Reference, normalize
from .regions import FrozenTileGrid, count_fixed_tiles, receiver_context
from .scoring import Score, score


@dataclass(frozen=True)
class GTFreeMeasurement:
    decision_id: str
    deadline_ns: int
    status: str
    counts: tuple[tuple[str, int], ...]
    outside_roi_count: int | None
    context_id: str | None
    context_reason: str
    region_digest: str
    units: str = "points"
    visibility: str = "unknown"


@dataclass(frozen=True)
class GTFreeDecision:
    measurement: GTFreeMeasurement
    spatial_penalty: float | None
    score: Score
    alarm: bool | None
    reference_id: str | None
    calibration_id: str | None

    def as_dict(self) -> dict:
        row = asdict(self)
        row["T"] = self.score.T
        row["score_status"] = self.score.status
        row["A"] = self.score.A_observed if self.score.status == "known" else None
        return row


def measure(*, decision_id: str, deadline_ns: int, available_ns: int | None,
            points_m: np.ndarray | None, grid: FrozenTileGrid,
            receiver_range_m: float | None, range_bins_m: tuple[float, ...],
            allow_broad_context: bool, message_state: str) -> GTFreeMeasurement:
    """Measure an already receiver-frame cloud at one sender/frame/deadline."""
    if grid.frozen_ns > deadline_ns:
        return GTFreeMeasurement(decision_id, deadline_ns, "unknown", (), None, None,
                                 "REGIONS_NOT_CAUSALLY_FROZEN", grid.digest)
    if message_state not in {"present_nonempty", "present_empty", "absent", "late", "malformed"}:
        raise ValueError("invalid message state")
    if message_state in {"absent", "late", "malformed"}:
        return GTFreeMeasurement(decision_id, deadline_ns, "unknown", (), None, None,
                                 "CLOUD_" + message_state.upper(), grid.digest)
    if available_ns is None or available_ns > deadline_ns or points_m is None:
        return GTFreeMeasurement(decision_id, deadline_ns, "unknown", (), None, None,
                                 "CLOUD_UNAVAILABLE", grid.digest)
    context_id, context_reason = receiver_context(
        receiver_range_m=receiver_range_m,
        range_bins_m=range_bins_m,
        allow_broad_context=allow_broad_context,
    )
    if context_id is None:
        return GTFreeMeasurement(decision_id, deadline_ns, "unknown", (), None, None,
                                 context_reason, grid.digest)
    counts, outside = count_fixed_tiles(points_m, grid)
    return GTFreeMeasurement(decision_id, deadline_ns, "known", tuple(counts.items()), outside,
                             context_id, context_reason, grid.digest)


def decide(measurement: GTFreeMeasurement, *, reference: Reference | None,
           kinematic_penalty: float | None, calibration: Calibration | None,
           reference_id: str | None, calibration_id: str | None) -> GTFreeDecision:
    """Normalize max tile surplus and combine with K using the frozen max rule."""
    if measurement.status != "known" or reference is None:
        reasons = (measurement.context_reason,) if measurement.status != "known" else ("REFERENCE_UNSUPPORTED",)
        result = score("vehicle", kinematic_penalty, None, reasons=reasons)
        return GTFreeDecision(measurement, None, result, None, reference_id, calibration_id)
    penalties = [(normalize(float(value), reference), region) for region, value in measurement.counts]
    spatial, strongest = max(penalties, key=lambda item: item[0])
    result = score("vehicle", kinematic_penalty, spatial, region=strongest)
    alarm_value = alarm(result.A_observed, calibration) if calibration is not None and result.status == "known" else None
    return GTFreeDecision(measurement, spatial, result, alarm_value, reference_id, calibration_id)


def score_clouds(cases: tuple[Mapping, ...], *, grid: FrozenTileGrid, reference: Reference,
                 calibration: Calibration, config: Mapping) -> tuple[GTFreeDecision, ...]:
    """Batch operational path used by tests and the S04 comparison."""
    output = []
    for case in cases:
        measurement = measure(
            decision_id=str(case["decision_id"]), deadline_ns=int(case["deadline_ns"]),
            available_ns=case.get("available_ns"), points_m=case.get("points_m"), grid=grid,
            receiver_range_m=case.get("receiver_range_m"),
            range_bins_m=tuple(config["receiver_context"]["range_bins_m"]),
            allow_broad_context=bool(config["receiver_context"]["allow_broad_context"]),
            message_state=str(case["message_state"]),
        )
        output.append(decide(
            measurement, reference=reference, kinematic_penalty=case.get("kinematic_penalty"),
            calibration=calibration, reference_id="gt_free.reference.v1",
            calibration_id="gt_free.calibration.v1",
        ))
    return tuple(output)
