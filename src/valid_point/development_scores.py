"""Exploratory one-segment reference and distinct R03 decision records."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import numpy as np

from valid_point.evidence.density import CELL_IDS
from valid_point.replay import RawFactorRecord


@dataclass(frozen=True)
class ExploratoryReference:
    stream: str
    factor: str
    context: str
    q50: float | None
    u: float | None
    b: float | None
    observations: int
    segment: str
    status: str
    row_ids: tuple[str, ...]
    reference_id: str


@dataclass(frozen=True)
class NormalizedFactors:
    cloud_id: str
    stream: str
    source_ns: int
    d: float | None
    g: float | None
    d_reason: str
    g_reason: str
    d_contexts: tuple[str, ...]
    g_context: str | None
    reference_id: str

    def as_dict(self): return asdict(self)


@dataclass(frozen=True)
class InstantaneousDecision:
    cloud_id: str
    stream: str
    principal: str
    source_ns: int
    arm: str
    status: str
    reason: str
    A: float | None
    C: float | None
    reference_id: str

    def as_dict(self): return asdict(self)


@dataclass(frozen=True)
class AlarmDecision:
    cloud_id: str
    stream: str
    principal: str
    source_ns: int
    arm: str
    status: str
    instant_alarm: bool | None
    temporal_alarm: bool | None
    threshold_id: str | None
    reason: str
    reference_id: str

    def as_dict(self): return asdict(self)


def _gap_context(gap_s: float | None) -> str | None:
    if gap_s is None or gap_s <= 0 or gap_s > .5: return None
    return "g0" if gap_s <= .15 else "g1" if gap_s <= .3 else "g2"


def fit_exploratory(records: list[RawFactorRecord], *, segment: str,
                    reference_id: str, min_rows: int = 50) -> dict[tuple[str,str,str], ExploratoryReference]:
    if min_rows < 50 or segment != "mini_7":
        raise ValueError("R03 exploratory support is >=50 actual rows from mini_7")
    groups: dict[tuple[str,str,str], list[tuple[str,float]]] = {}
    for row in records:
        if row.density.counts is not None:
            for cell,value in zip(CELL_IDS,row.density.counts):
                groups.setdefault((row.stream,"D",cell),[]).append((row.cloud_id,float(value)))
                groups.setdefault((row.stream,"D","range:"+cell.split(":")[0]),[]).append((row.cloud_id,float(value)))
        if row.geometry.distance_m is not None:
            groups.setdefault((row.stream,"G","all"),[]).append((row.cloud_id,row.geometry.distance_m))
            context=_gap_context(row.geometry.gap_s)
            if context is not None:
                groups.setdefault((row.stream,"G",context),[]).append((row.cloud_id,row.geometry.distance_m))
    result={}
    for key,values in groups.items():
        sample=np.asarray([v for _,v in values])
        distinct_cloud_rows=len({cloud_id for cloud_id,_ in values})
        q50,u=map(float,np.quantile(sample,[.5,.95],method="linear"))
        b=4*(u-q50)
        status="supported_exploratory" if distinct_cloud_rows>=min_rows and b>0 else "zero_scale" if b<=0 else "low_support"
        result[key]=ExploratoryReference(*key,q50,u,b,len(values),segment,status,
                                          tuple(x for x,_ in values),reference_id)
    return result


def normalize_raw(row: RawFactorRecord, refs: dict, reference_id: str) -> NormalizedFactors:
    ds=[]; used=[]; d_reason=row.density.reason
    if row.density.counts is not None:
        for cell,count in zip(CELL_IDS,row.density.counts):
            ref=refs.get((row.stream,"D",cell))
            if ref is None or ref.status!="supported_exploratory":
                ref=refs.get((row.stream,"D","range:"+cell.split(":")[0]))
            if ref is None or ref.status!="supported_exploratory":
                d_reason="UNSUPPORTED_CELL:"+cell; break
            ds.append(float(np.clip((count-ref.u)/ref.b,0,1))); used.append(ref.context)
        else: d_reason="VALID"
    d=max(ds) if d_reason=="VALID" and len(ds)==len(CELL_IDS) else None
    g=None; gc=None; g_reason=row.geometry.reason
    if row.geometry.distance_m is not None:
        context=_gap_context(row.geometry.gap_s)
        ref=refs.get((row.stream,"G",context)) if context else None
        if ref is None or ref.status!="supported_exploratory": ref=refs.get((row.stream,"G","all"))
        if ref is not None and ref.status=="supported_exploratory":
            g=float(np.clip((row.geometry.distance_m-ref.u)/ref.b,0,1)); gc=ref.context; g_reason="VALID"
        else: g_reason="UNSUPPORTED_G_REFERENCE"
    return NormalizedFactors(row.cloud_id,row.stream,row.source_ns,d,g,d_reason,g_reason,tuple(used),gc,reference_id)


def decide(row: RawFactorRecord, factors: NormalizedFactors, arm: str) -> InstantaneousDecision:
    required={"D-only":(factors.d,),"G-only":(factors.g,),"max(D,G)":(factors.d,factors.g)}
    if arm not in required: raise ValueError("unknown arm")
    known=all(x is not None for x in required[arm])
    A=max(required[arm]) if known else None
    why="VALID" if known else ";".join(x for x in (factors.d_reason if factors.d is None else "",factors.g_reason if factors.g is None and arm!="D-only" else "") if x)
    return InstantaneousDecision(row.cloud_id,row.stream,row.principal,row.source_ns,arm,
                                  "known" if known else "unknown",why,A,None if A is None else 1-A,factors.reference_id)
