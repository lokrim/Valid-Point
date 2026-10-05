"""S01 causal records. No scoring or evaluator labels live in these records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

import numpy as np


class MessageState(str, Enum):
    PRESENT_NONEMPTY = "present_nonempty"
    PRESENT_EMPTY = "present_empty"
    ABSENT = "absent"
    LATE = "late"
    MALFORMED = "malformed"


class EvidenceStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
    INVALID = "invalid"


@dataclass(frozen=True)
class DecisionKey:
    episode: str
    sender: str
    frame_id: int
    deadline_ns: int

    def __post_init__(self) -> None:
        if not self.episode or not self.sender or self.frame_id < 0 or self.deadline_ns < 0:
            raise ValueError("invalid decision key")


@dataclass(frozen=True)
class RigidTransform:
    transform_id: str
    source_frame: str
    target_frame: str
    matrix: tuple[tuple[float, float, float, float], ...]
    valid_from_ns: int
    valid_until_ns: int
    provenance: str
    units: Literal["m"] = "m"
    handedness: Literal["right"] = "right"
    quaternion_order: Literal["xyzw"] = "xyzw"

    def __post_init__(self) -> None:
        m = np.asarray(self.matrix, dtype=float)
        if (not self.transform_id or not self.source_frame or not self.target_frame
                or not self.provenance or self.valid_from_ns > self.valid_until_ns
                or m.shape != (4, 4) or not np.isfinite(m).all()
                or not np.allclose(m[3], [0, 0, 0, 1], atol=1e-12)
                or not np.allclose(m[:3, :3].T @ m[:3, :3], np.eye(3), atol=1e-12)
                or not np.isclose(np.linalg.det(m[:3, :3]), 1, atol=1e-12)):
            raise ValueError("invalid rigid transform")

    def apply(self, xyz: np.ndarray, *, inverse: bool = False) -> np.ndarray:
        points = np.asarray(xyz, dtype=float)
        if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
            raise ValueError("xyz must be finite N x 3")
        m = np.asarray(self.matrix)
        if inverse:
            m = np.linalg.inv(m)
        return points @ m[:3, :3].T + m[:3, 3]


@dataclass(frozen=True)
class CausalSample:
    sample_id: str
    source_ns: int
    available_ns: int
    position_m: tuple[float, float, float] | None
    velocity_mps: tuple[float, float, float] | None

    def __post_init__(self) -> None:
        if not self.sample_id or self.source_ns < 0 or self.available_ns < self.source_ns:
            raise ValueError("invalid causal sample clock or ID")
        for vector in (self.position_m, self.velocity_mps):
            if vector is not None and (len(vector) != 3 or not np.isfinite(vector).all()):
                raise ValueError("nonfinite causal vector")


@dataclass(frozen=True)
class DecisionInput:
    key: DecisionKey
    sensor_id: str
    security_group: str
    sensor_role: Literal["static_rsu", "vehicle"]
    anchor_ns: int
    source_ns: int | None
    arrival_ns: int | None
    message_state: MessageState
    cloud_id: str | None
    point_count: int | None
    transform_id: str | None
    samples: tuple[CausalSample, ...] = ()
    visibility: Literal["unknown"] = "unknown"

    def __post_init__(self) -> None:
        if not self.sensor_id or not self.security_group or self.anchor_ns > self.key.deadline_ns:
            raise ValueError("invalid sensor or deadline")
        if self.anchor_ns < 0 or (self.source_ns is not None and self.source_ns < 0):
            raise ValueError("negative decision clock")
        if self.arrival_ns is not None and self.arrival_ns < 0:
            raise ValueError("negative arrival clock")
        if self.source_ns is not None and self.source_ns > self.key.deadline_ns:
            raise ValueError("future source time")
        if len({s.sample_id for s in self.samples}) != len(self.samples):
            raise ValueError("duplicate causal sample IDs")
        if any(s.source_ns > self.key.deadline_ns or s.available_ns > self.key.deadline_ns
               or s.source_ns > s.available_ns for s in self.samples):
            raise ValueError("future or unavailable sample")
        if self.message_state in (MessageState.PRESENT_NONEMPTY, MessageState.PRESENT_EMPTY):
            if (self.arrival_ns is None or self.arrival_ns > self.key.deadline_ns
                    or self.cloud_id is None or self.point_count is None):
                raise ValueError("present cloud must be available by deadline")
            if self.message_state is MessageState.PRESENT_NONEMPTY and self.point_count <= 0:
                raise ValueError("nonempty cloud requires positive count")
            if self.message_state is MessageState.PRESENT_EMPTY and self.point_count != 0:
                raise ValueError("empty cloud requires zero count")
        elif self.message_state is MessageState.ABSENT:
            if self.arrival_ns is not None or self.cloud_id is not None or self.point_count is not None:
                raise ValueError("absent message has no cloud or arrival")
        elif self.message_state is MessageState.LATE:
            if self.arrival_ns is None or self.arrival_ns <= self.key.deadline_ns or self.point_count is not None:
                raise ValueError("late cloud is unavailable at decision time")
        elif self.message_state is MessageState.MALFORMED:
            if self.arrival_ns is None or self.arrival_ns > self.key.deadline_ns or self.point_count is not None:
                raise ValueError("malformed cloud cannot have a parsed count")


def assert_unique_keys(inputs: tuple[DecisionInput, ...] | list[DecisionInput]) -> None:
    keys = [row.key for row in inputs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate decision keys")


@dataclass(frozen=True)
class RawMeasurement:
    key: DecisionKey
    name: str
    value: float | None
    unit: str
    status: EvidenceStatus
    reason: str
    available_ns: int | None
    source_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status is EvidenceStatus.KNOWN and (self.value is None or not np.isfinite(self.value)):
            raise ValueError("known measurement requires finite value")
        if self.status is not EvidenceStatus.KNOWN and self.value is not None:
            raise ValueError("unknown/inapplicable/invalid value must be null")
        if self.available_ns is not None and self.available_ns > self.key.deadline_ns:
            raise ValueError("measurement after deadline")


@dataclass(frozen=True)
class NormalizedEvidence:
    key: DecisionKey
    factor: str
    penalty: float | None
    status: EvidenceStatus
    raw_ids: tuple[str, ...]
    reference_id: str | None

    def __post_init__(self) -> None:
        if self.status is EvidenceStatus.KNOWN:
            if self.penalty is None or not 0 <= self.penalty <= 1 or not self.reference_id:
                raise ValueError("known normalized evidence requires bounded penalty and reference")
        elif self.penalty is not None:
            raise ValueError("unknown normalized evidence must have null penalty")


@dataclass(frozen=True)
class ScoreRecord:
    key: DecisionKey
    conformity: float | None
    status: EvidenceStatus
    track: Literal["gt_free", "oracle_box"]
    reason: str

    def __post_init__(self) -> None:
        if self.status is EvidenceStatus.KNOWN:
            if self.conformity is None or not 0 <= self.conformity <= 1:
                raise ValueError("known conformity must be within [0,1]")
        elif self.conformity is not None:
            raise ValueError("unknown conformity must be null")


@dataclass(frozen=True)
class AlarmRecord:
    key: DecisionKey
    alarm: bool | None
    calibration_id: str | None
    state: str


@dataclass(frozen=True)
class AllocationRecord:
    based_on: DecisionKey
    effective_frame_id: int
    bytes_allowed: int
    policy_id: str

    def __post_init__(self) -> None:
        if self.effective_frame_id <= self.based_on.frame_id or self.bytes_allowed < 0:
            raise ValueError("allocation must apply to a future frame")
