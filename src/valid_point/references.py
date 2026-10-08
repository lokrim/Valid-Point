"""Clean-only contextual upper references for S03 illustrative raw observations."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, asdict
from math import isfinite
import numpy as np


@dataclass(frozen=True)
class Reference:
    factor: str
    context: str
    level: str
    n: int
    segments: tuple[str, ...]
    q50: float
    u: float
    b: float
    units: str
    status: str


def context_chain(factor: str, sensor: str, bin_id: str, *, pooled: bool = False) -> tuple[str, ...]:
    if factor not in ('K', 'S') or not sensor or not bin_id:
        raise ValueError('invalid reference context')
    # Pooled is opt-in because sensor semantics and units may differ.
    return (f'{factor}:{sensor}:{bin_id}', f'{factor}:{sensor}') + ((f'{factor}:pooled',) if pooled else ())


def fit_references(rows: list[dict], *, min_rows: int = 200, min_segments: int = 2,
                   allowed_seeds: set[int] | None = None, pooled_compatible: bool = False) -> dict[str, Reference]:
    """Fit linear empirical q50/q95 on reference-role rows only; retain failures."""
    if min_rows < 1 or min_segments < 2:
        raise ValueError('invalid support rule')
    groups: dict[str, list[dict]] = defaultdict(list)
    seen = set()
    for row in rows:
        if row['split_role'] != 'reference' or row.get('clean') is not True:
            raise ValueError('reference fit accepts only declared clean reference rows')
        if allowed_seeds is not None and row['seed'] not in allowed_seeds:
            raise ValueError('reference seed not in frozen lineage')
        key = (row['seed'], row['frame'], row['factor'], row['region_id'])
        if key in seen:
            raise ValueError('duplicate raw reference observation')
        seen.add(key)
        value = row['value']
        if value is None or not isfinite(value) or value < 0:
            raise ValueError('reference raw value invalid')
        factor = row['factor']
        units = {'K': 'm', 'S': 'points'}[factor]
        if row['units'] != units:
            raise ValueError('reference units mismatch')
        contexts = context_chain(factor, row['sensor_class'], row['bin_id'], pooled=pooled_compatible)
        for context in contexts:
            groups[context].append(row)
    result = {}
    for context, sample in sorted(groups.items()):
        factors = {r['factor'] for r in sample}
        if len(factors) != 1:
            raise ValueError('mixed factors')
        values = np.asarray([r['value'] for r in sample], dtype=float)
        q50, q95 = (float(x) for x in np.quantile(values, [.5, .95], method='linear'))
        b = 4 * (q95 - q50)
        segments = tuple(sorted({str(r['segment']) for r in sample}))
        status = 'supported' if len(sample) >= min_rows and len(segments) >= min_segments and b > 0 else (
            'zero_scale' if b <= 0 else 'low_support')
        level = 'specific' if context.count(':') == 2 else ('pooled' if context.endswith(':pooled') else 'sensor')
        result[context] = Reference(next(iter(factors)), context, level, len(sample), segments,
                                    q50, q95, b, sample[0]['units'], status)
    return result


def select_reference(bundle: dict[str, Reference], factor: str, sensor: str, bin_id: str,
                     *, pooled_compatible: bool = False) -> tuple[Reference | None, str]:
    chain = context_chain(factor, sensor, bin_id, pooled=pooled_compatible)
    for index, context in enumerate(chain):
        ref = bundle.get(context)
        if ref is not None and ref.status == 'supported':
            return ref, 'direct' if index == 0 else 'fallback'
    return None, 'REFERENCE_UNSUPPORTED'


def normalize(value: float | None, reference: Reference | None) -> float | None:
    if value is None or reference is None or reference.status != 'supported':
        return None
    if not isfinite(value) or value < 0 or reference.b <= 0:
        raise ValueError('invalid normalization input')
    return float(np.clip((value - reference.u) / reference.b, 0, 1))


def reference_rows(bundle: dict[str, Reference]) -> list[dict]:
    return [asdict(ref) for ref in bundle.values()]
