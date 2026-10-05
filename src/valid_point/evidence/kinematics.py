"""Causal zero-order motion self-consistency, in metres; no normalization."""
from dataclasses import dataclass

import numpy as np

from valid_point.contracts import DecisionKey, EvidenceStatus as Status, RawMeasurement


@dataclass(frozen=True)
class MotionSample:
    sample_id: str
    source_ns: int
    available_ns: int
    position: tuple[float, float, float] | None
    velocity: tuple[float, float, float] | None
    # R maps body-frame velocity to the position frame at this sample's time.
    rotation: tuple[tuple[float, float, float], ...] | None
    position_frame: str = "receiver"
    velocity_frame: str = "body"
    position_unit: str = "m"
    velocity_unit: str = "m/s"
    provenance: str = "sender report; not independent motion evidence"


@dataclass(frozen=True)
class MotionResult:
    residual: RawMeasurement
    dt_s: float | None
    displacement_m: tuple[float, ...] | None
    predicted_displacement_m: tuple[float, ...] | None
    residual_vector_m: tuple[float, ...] | None
    selected_ids: tuple[str, ...]
    excluded: tuple[tuple[str, str], ...]


def measure_motion(key: DecisionKey, samples: tuple[MotionSample, ...], *,
                   anchor_ns: int, sensor_role: str = "vehicle", max_age_ns: int,
                   min_dt_s: float, max_dt_s: float, clock_verified: bool = True) -> MotionResult:
    """Latest two samples at/before anchor, received by deadline, without value-based fallback.

    A sample at a future source time or received after the deadline is never used.
    Unknown fields in the selected pair do not cause a search for a more favorable pair.
    """
    if not (0 <= anchor_ns <= key.deadline_ns and max_age_ns >= 0
            and np.isfinite([min_dt_s, max_dt_s]).all() and 0 < min_dt_s <= max_dt_s):
        raise ValueError("invalid motion engineering bounds")
    if sensor_role not in ("vehicle", "static_rsu"):
        raise ValueError("unsupported sensor role")
    selected = ()
    excluded = []
    dt = None

    def result(status, reason, value=None, displacement=None, predicted=None, vector=None):
        ids = tuple(s.sample_id for s in selected)
        available = max((s.available_ns for s in selected), default=None)
        return MotionResult(RawMeasurement(key, "motion_residual", value, "m", status,
                                          reason, available, ids), dt, displacement,
                            predicted, vector, ids, tuple(excluded))

    if sensor_role == "static_rsu":
        return result(Status.NOT_APPLICABLE, "NOT_APPLICABLE_STATIC")
    if not clock_verified:
        return result(Status.UNKNOWN, "CLOCK_UNVERIFIED")
    if len({s.sample_id for s in samples}) != len(samples):
        return result(Status.INVALID, "DUPLICATE_SAMPLE_ID")
    causal = []
    for sample in samples:
        if (not sample.sample_id or type(sample.source_ns) is not int
                or type(sample.available_ns) is not int or sample.source_ns < 0
                or sample.available_ns < sample.source_ns):
            return result(Status.INVALID, "MALFORMED_SAMPLE_CLOCK")
        reason = ("FUTURE_SAMPLE" if sample.source_ns > anchor_ns else
                  "LATE" if sample.available_ns > key.deadline_ns else
                  "STALE_SAMPLE" if anchor_ns - sample.source_ns > max_age_ns else None)
        if reason:
            excluded.append((sample.sample_id, reason))
        else:
            causal.append(sample)
    selected = tuple(sorted(causal, key=lambda s: (s.source_ns, s.sample_id))[-2:])
    if len(selected) < 2:
        return result(Status.UNKNOWN, "INSUFFICIENT_CAUSAL_SAMPLES")
    prior, current = selected
    dt = (current.source_ns - prior.source_ns) / 1e9
    if not min_dt_s <= dt <= max_dt_s:
        return result(Status.INVALID, "INVALID_DT")
    if any(s.position_frame != "receiver" or s.position_unit != "m" for s in selected):
        return result(Status.UNKNOWN, "UNSUPPORTED_POSITION_CONVENTION")
    if prior.velocity_frame not in ("body", "receiver") or prior.velocity_unit != "m/s":
        return result(Status.UNKNOWN, "UNSUPPORTED_VELOCITY_CONVENTION")
    if prior.position is None or current.position is None:
        return result(Status.UNKNOWN, "POSITION_MISSING")
    if prior.velocity is None:
        return result(Status.UNKNOWN, "VELOCITY_MISSING")
    if prior.velocity_frame == "body" and prior.rotation is None:
        return result(Status.UNKNOWN, "ORIENTATION_MISSING")
    try:
        p0, p1, v0 = [np.asarray(v, dtype=float) for v in
                      (prior.position, current.position, prior.velocity)]
        rotation = np.eye(3) if prior.velocity_frame == "receiver" else np.asarray(prior.rotation, dtype=float)
        if any(v.shape != (3,) or not np.isfinite(v).all() for v in (p0, p1, v0)):
            return result(Status.INVALID, "MALFORMED_MOTION_VECTOR")
        if (rotation.shape != (3, 3) or not np.isfinite(rotation).all()
                or not np.allclose(rotation.T @ rotation, np.eye(3), rtol=0, atol=1e-9)
                or not np.isclose(np.linalg.det(rotation), 1, rtol=0, atol=1e-9)):
            return result(Status.INVALID, "ORIENTATION_INVALID")
    except (ValueError, TypeError):
        return result(Status.INVALID, "MALFORMED_MOTION_FIELDS")
    displacement = p1 - p0
    predicted = rotation @ v0 * dt
    vector = displacement - predicted
    residual = float(np.linalg.norm(vector))
    if not np.isfinite(residual):
        return result(Status.INVALID, "NONFINITE_RESIDUAL")
    return result(Status.KNOWN, "SELF_REPORT_ONLY", residual,
                  tuple(displacement), tuple(predicted), tuple(vector))
