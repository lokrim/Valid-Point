"""Weight-free sender/frame conformity with strict unknown coverage."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from .references import Reference, normalize


@dataclass(frozen=True)
class Score:
    status: str
    T: float | None
    lower: float
    upper: float
    A_observed: float
    strongest_factor: str | None
    strongest_region: str | None
    reasons: tuple[str, ...]
    required: tuple[str, ...]


def spatial_penalty(regions: dict[str, tuple[float | None, Reference | None]],
                    required_regions: tuple[str, ...]) -> tuple[float | None, str | None, tuple[str, ...]]:
    if not required_regions:
        return None, None, ('NO_REGION',)
    penalties = []
    reasons = []
    for region in required_regions:
        if region not in regions or regions[region][0] is None:
            reasons.append('REGION_UNKNOWN:' + region)
            continue
        value, ref = regions[region]
        penalty = normalize(value, ref)
        if penalty is None:
            reasons.append('REFERENCE_UNSUPPORTED:' + region)
        else:
            penalties.append((penalty, region))
    strongest = max(penalties, key=lambda pair: pair[0]) if penalties else (None, None)
    if reasons:
        return None, strongest[1], tuple(reasons + (['SCORE_PARTIAL'] if penalties else []))
    return strongest[0], strongest[1], ()


def spatial_diagnostic(regions: dict[str, tuple[float | None, Reference | None]],
                       required_regions: tuple[str, ...]) -> dict:
    """Retain partial measured S separately from the full eligibility result."""
    full, strongest, reasons = spatial_penalty(regions, required_regions)
    observed = []
    for region in required_regions:
        if region in regions and regions[region][0] is not None:
            penalty = normalize(*regions[region])
            if penalty is not None:
                observed.append((penalty, region))
    partial = max(observed, key=lambda pair: pair[0]) if observed else (None, None)
    return {'S': full, 'partial_max': partial[0], 'partial_region': partial[1],
            'strongest_region': strongest, 'reasons': reasons,
            'coverage_known': full is not None}


def score(sensor_role: str, K: float | None, S: float | None, *, region: str | None = None,
          reasons: tuple[str, ...] = ()) -> Score:
    if sensor_role not in ('vehicle', 'static_rsu'):
        raise ValueError('sensor role must be preregistered')
    for value in (K, S):
        if value is not None and (not isfinite(value) or not 0 <= value <= 1):
            raise ValueError('penalty outside [0,1]')
    required = ('K', 'S') if sensor_role == 'vehicle' else ('S',)
    values = {'K': K, 'S': S}
    known = [(factor, values[factor]) for factor in required if values[factor] is not None]
    strongest = max(known, key=lambda pair: pair[1]) if known else (None, 0.0)
    if len(known) == 2 and known[0][1] == known[1][1]:
        strongest = ('K+S', known[0][1])
    anomaly = float(strongest[1])
    missing = tuple(f'{factor}_UNKNOWN' for factor in required if values[factor] is None)
    why = tuple(dict.fromkeys(reasons + missing + (('NOT_APPLICABLE_STATIC',) if sensor_role == 'static_rsu' else ())))
    if missing:
        return Score('unknown', None, 0.0, 1 - anomaly, anomaly, strongest[0],
                     region if strongest[0] in ('S', 'K+S') else None, why, required)
    return Score('known', 1 - anomaly, 1 - anomaly, 1 - anomaly, anomaly,
                 strongest[0], region if strongest[0] in ('S', 'K+S') else None, why, required)
