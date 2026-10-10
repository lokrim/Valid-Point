"""R02 operational wrapper superseding S04's illustrative gt_free.score_clouds.

It measures through the causal replay reader. Optional references are supplied
externally; mini_7 R02 does not fit or use a final reference.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from valid_point.replay import AllowedSource, CloudEvent, RawFactorRecord, ReplayConfig, replay

@dataclass(frozen=True)
class DCellReference:
    cell_id: str
    upper_points: float
    scale_points: float
    observations: int
    segments: int
    reference_id: str

@dataclass(frozen=True)
class OperationalRecord:
    raw: RawFactorRecord
    d_anomaly: float | None
    d_status: str
    d_reason: str
    reference_id: str | None

    def as_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)


def _d_normalize(raw: RawFactorRecord, reference: tuple[DCellReference,...] | None) -> tuple[float | None,str,str,str | None]:
    from valid_point.evidence.density import CELL_IDS
    if raw.density.counts is None:
        return None,"unknown",raw.density.reason,None
    if reference is None:
        return None,"unknown","REFERENCE_NOT_FIT",None
    refs={r.cell_id:r for r in reference}
    if len(reference)!=len(CELL_IDS) or set(refs)!=set(CELL_IDS):
        return None,"unknown","REQUIRED_CELL_COVERAGE",None
    if len({r.reference_id for r in reference})!=1:
        return None,"invalid","MIXED_REFERENCE_IDS",None
    if any(r.observations<200 or r.segments<2 for r in reference):
        return None,"unknown","ZERO_OR_INSUFFICIENT_REFERENCE_SUPPORT",reference[0].reference_id
    if any(r.scale_points<=0 or r.upper_points<0 for r in reference):
        return None,"unknown","ZERO_OR_INVALID_REFERENCE_SCALE",reference[0].reference_id
    values=[max(0.,min(1.,(n-refs[cell].upper_points)/refs[cell].scale_points)) for cell,n in zip(CELL_IDS,raw.density.counts)]
    return max(values),"known","VALID",reference[0].reference_id


def measure_operational(events: Iterable[CloudEvent], source: AllowedSource, *,
                        config: ReplayConfig=ReplayConfig(),
                        reference: tuple[DCellReference,...] | None=None,
                        poses=None) -> tuple[OperationalRecord,...]:
    return tuple(OperationalRecord(raw,*_d_normalize(raw,reference))
                 for raw in replay(events,source,config=config,poses=poses))
