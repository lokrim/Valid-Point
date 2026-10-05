"""Receiver-observed availability and explicit independent eligibility states."""
from dataclasses import dataclass

from valid_point.contracts import (DecisionInput, EvidenceStatus as Status,
                                   MessageState, RawMeasurement, RigidTransform)
from valid_point.io.pointcloud import PointCloud


@dataclass(frozen=True)
class ReceiverContext:
    context_id: str
    available_ns: int
    provenance: str
    clock_verified: bool = True
    membership_verified: bool = True
    health: str = "unknown"  # only independently observed healthy/fault is accepted
    transform: RigidTransform | None = None
    transform_available_ns: int | None = None

    def __post_init__(self):
        if (not self.context_id or not self.provenance or type(self.available_ns) is not int
                or type(self.clock_verified) is not bool or type(self.membership_verified) is not bool
                or self.available_ns < 0
                or self.health not in ("unknown", "healthy", "fault")
                or (self.transform_available_ns is not None and self.transform_available_ns < 0)):
            raise ValueError("invalid receiver context")


@dataclass(frozen=True)
class Eligibility:
    status: Status
    reason: str


@dataclass(frozen=True)
class Availability:
    message_state: str
    freshness: RawMeasurement
    payload: Eligibility
    transform: Eligibility
    health: Eligibility
    membership: Eligibility
    eligible: Eligibility
    context_id: str
    provenance: str


def measure_availability(row: DecisionInput, cloud: PointCloud | None,
                         context: ReceiverContext, *, max_cloud_age_ns: int) -> Availability:
    """Freshness is deadline minus source time; health is never inferred from content.

    Payload/transform eligibility may permit raw counts while overall eligibility
    stays unknown for unverified health or membership. No state expresses intent.
    """
    if max_cloud_age_ns < 0:
        raise ValueError("negative freshness bound")
    known = Eligibility(Status.KNOWN, "VALID")
    context_causal = context.available_ns <= row.key.deadline_ns
    if not context_causal or not context.clock_verified:
        freshness = RawMeasurement(row.key, "source_age", None, "s", Status.UNKNOWN,
                                   "CLOCK_UNVERIFIED", None, ())
    elif row.message_state in (MessageState.ABSENT, MessageState.LATE):
        freshness = RawMeasurement(row.key, "source_age", None, "s", Status.UNKNOWN,
                                   "SOURCE_TIME_UNAVAILABLE", row.key.deadline_ns, (context.context_id,))
    elif row.source_ns is None:
        freshness = RawMeasurement(row.key, "source_age", None, "s", Status.UNKNOWN,
                                   "SOURCE_TIME_MISSING", row.key.deadline_ns, (context.context_id,))
    elif row.source_ns > row.anchor_ns:
        freshness = RawMeasurement(row.key, "source_age", None, "s", Status.INVALID,
                                   "FUTURE_SAMPLE", row.key.deadline_ns, (context.context_id,))
    else:
        age = row.key.deadline_ns - row.source_ns
        freshness = RawMeasurement(row.key, "source_age", age / 1e9, "s", Status.KNOWN,
                                   "FRESH" if age <= max_cloud_age_ns else "STALE",
                                   row.key.deadline_ns, (context.context_id,))
    if row.message_state == MessageState.ABSENT:
        payload = Eligibility(Status.UNKNOWN, "CLOUD_ABSENT")
    elif row.message_state == MessageState.LATE:
        payload = Eligibility(Status.UNKNOWN, "LATE")
    elif row.message_state == MessageState.MALFORMED:
        payload = Eligibility(Status.INVALID, "MALFORMED")
    elif cloud is None:
        payload = Eligibility(Status.UNKNOWN, "CLOUD_MISSING")
    elif cloud.count != row.point_count:
        payload = Eligibility(Status.INVALID, "COUNT_MISMATCH")
    elif row.source_ns is not None and row.arrival_ns < row.source_ns:
        payload = Eligibility(Status.INVALID, "ARRIVAL_BEFORE_SOURCE")
    elif freshness.status != Status.KNOWN:
        payload = Eligibility(freshness.status, freshness.reason)
    elif freshness.reason == "STALE":
        payload = Eligibility(Status.UNKNOWN, "STALE")
    else:
        payload = known
    t = context.transform
    if (not context_causal or t is None or context.transform_available_ns is None
            or context.transform_available_ns > row.key.deadline_ns):
        transform = Eligibility(Status.UNKNOWN, "TRANSFORM_UNAVAILABLE")
    elif (t.transform_id != row.transform_id or t.target_frame != "receiver"
          or (cloud is not None and t.source_frame != cloud.frame)
          or t.units != "m" or t.handedness != "right" or t.quaternion_order != "xyzw"):
        transform = Eligibility(Status.UNKNOWN, "TRANSFORM_UNSUPPORTED")
    elif row.source_ns is None or row.message_state in (MessageState.ABSENT, MessageState.LATE):
        transform = Eligibility(Status.UNKNOWN, "TRANSFORM_TIME_UNKNOWN")
    elif not t.valid_from_ns <= row.source_ns <= t.valid_until_ns:
        transform = Eligibility(Status.INVALID, "TRANSFORM_INVALID")
    else:
        transform = known
    health = (Eligibility(Status.UNKNOWN, "SENSOR_HEALTH_UNKNOWN")
              if not context_causal or context.health == "unknown" else
              Eligibility(Status.INVALID, "SENSOR_FAULT") if context.health == "fault" else known)
    membership = (known if context_causal and context.membership_verified else
                  Eligibility(Status.UNKNOWN, "MEMBERSHIP_UNKNOWN"))
    components = (payload, transform, health, membership)
    eligible = next((s for s in components if s.status == Status.INVALID),
                    next((s for s in components if s.status != Status.KNOWN), known))
    return Availability(row.message_state.value, freshness, payload, transform, health,
                        membership, eligible, context.context_id, context.provenance)
