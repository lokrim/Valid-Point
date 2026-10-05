"""Counts in externally frozen half-open boxes, including empty boxes; no score."""
from dataclasses import dataclass

import numpy as np

from valid_point.contracts import DecisionInput, EvidenceStatus as Status, RawMeasurement
from valid_point.io.pointcloud import PointCloud
from .availability import ReceiverContext, measure_availability


@dataclass(frozen=True)
class FixedRegion:
    region_id: str
    lower_m: tuple[float, float, float]
    upper_m: tuple[float, float, float]

    def __post_init__(self):
        lo, hi = np.asarray(self.lower_m), np.asarray(self.upper_m)
        if (not self.region_id or lo.shape != (3,) or hi.shape != (3,)
                or not np.isfinite([lo, hi]).all() or not (hi > lo).all()):
            raise ValueError("invalid fixed region")

    @property
    def volume_m3(self):
        return float(np.prod(np.asarray(self.upper_m) - self.lower_m))


@dataclass(frozen=True)
class RegionSet:
    regions: tuple[FixedRegion, ...]
    track: str
    authority: str
    provenance: str
    frozen_ns: int
    frame: str = "receiver"

    def __post_init__(self):
        if (self.track, self.authority) not in (("gt_free", "receiver"), ("oracle_box", "evaluator")):
            raise ValueError("region namespace/authority mismatch")
        if (not self.provenance or self.frozen_ns < 0
                or len({r.region_id for r in self.regions}) != len(self.regions)):
            raise ValueError("invalid region provenance/IDs")
        if any(not r.region_id.startswith(self.track + ":") for r in self.regions):
            raise ValueError("region ID must carry its track namespace")


@dataclass(frozen=True)
class SpatialResult:
    counts: tuple[RawMeasurement, ...]
    outside_regions: RawMeasurement
    coverage_status: Status
    reason: str
    track: str
    region_provenance: str
    visibility: str = "unknown"
    deficit_inference: str = "unknown: visibility not independently established"


def count_regions(row: DecisionInput, cloud: PointCloud | None, regions: RegionSet,
                  context: ReceiverContext, *, max_cloud_age_ns: int) -> SpatialResult:
    availability = measure_availability(row, cloud, context, max_cloud_age_ns=max_cloud_age_ns)
    state = next((s for s in (availability.payload, availability.transform)
                  if s.status != Status.KNOWN), None)
    status, reason = (state.status, state.reason) if state else (Status.KNOWN, "FIXED_REGION_COUNT")
    if not regions.regions:
        status, reason = Status.UNKNOWN, "NO_REGION"
    elif regions.frozen_ns > row.anchor_ns:
        status, reason = Status.UNKNOWN, "REGIONS_NOT_CAUSALLY_FROZEN"
    elif regions.frame != "receiver":
        status, reason = Status.UNKNOWN, "REGION_FRAME_UNSUPPORTED"
    source_ids = tuple(x for x in (row.cloud_id, row.transform_id, context.context_id) if x)
    available = (max(row.arrival_ns, context.available_ns, context.transform_available_ns,
                     regions.frozen_ns) if status == Status.KNOWN else None)

    def measurement(name, value, ids=()):
        return RawMeasurement(row.key, name, value, "points", status, reason, available, source_ids + ids)

    if status != Status.KNOWN:
        return SpatialResult(tuple(measurement(r.region_id, None, (r.region_id,)) for r in regions.regions),
                             measurement("outside_regions", None), status, reason,
                             regions.track, regions.provenance)
    xyz = context.transform.apply(cloud.xyz())
    covered = np.zeros(len(xyz), dtype=bool)
    counts = []
    for region in regions.regions:
        inside = ((xyz >= region.lower_m) & (xyz < region.upper_m)).all(axis=1)
        covered |= inside
        counts.append(measurement(region.region_id, int(inside.sum()), (region.region_id,)))
    return SpatialResult(tuple(counts), measurement("outside_regions", int((~covered).sum())),
                         status, reason, regions.track, regions.provenance)
