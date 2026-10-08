"""Separate clean operating calibration; alarm only for known A > c."""
from __future__ import annotations
from dataclasses import dataclass
from math import ceil, sqrt


@dataclass(frozen=True)
class Calibration:
    status: str
    alpha: float
    threshold: float | None
    known_n: int
    all_n: int
    order_index: int | None
    achieved_fpr: float | None
    abstention: float
    wilson_low: float | None
    wilson_high: float | None
    segments: tuple[str, ...]
    no_power: bool


def _wilson(success: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = success / n
    center = (p + z*z/(2*n)) / (1 + z*z/n)
    radius = z * sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return max(0, center-radius), min(1, center+radius)


def calibrate(rows: list[dict], *, alpha: float = .01, min_known: int = 200,
              allowed_seeds: set[int] | None = None) -> Calibration:
    if not 0 < alpha < 1 or min_known < 1 or not rows:
        raise ValueError('invalid calibration request')
    scores = []
    segments = set()
    for row in rows:
        if row['split_role'] != 'calibration' or row.get('clean') is not True:
            raise ValueError('calibration accepts separate clean calibration rows only')
        if allowed_seeds is not None and row['seed'] not in allowed_seeds:
            raise ValueError('calibration seed outside frozen lineage')
        segments.add(str(row['segment']))
        if row['status'] == 'known':
            value = row['A']
            if value is None or not 0 <= value <= 1:
                raise ValueError('invalid known anomaly')
            scores.append(value)
        elif row['status'] != 'unknown' or row['A'] is not None:
            raise ValueError('unknown row cannot carry an operating score')
    n = len(scores)
    abstention = 1 - n/len(rows)
    if n < min_known:
        return Calibration('unavailable', alpha, None, n, len(rows), None, None,
                           abstention, None, None, tuple(sorted(segments)), True)
    index = ceil((n+1)*(1-alpha))
    threshold = 1.0 if index > n else sorted(scores)[index-1]
    alarms = sum(value > threshold for value in scores)
    low, high = _wilson(alarms, n)
    return Calibration('available', alpha, threshold, n, len(rows), index,
                       alarms/n, abstention, low, high, tuple(sorted(segments)), threshold == 1)


def alarm(anomaly: float | None, calibration: Calibration) -> bool | None:
    if anomaly is None or calibration.status != 'available':
        return None
    if not 0 <= anomaly <= 1:
        raise ValueError('invalid anomaly')
    return anomaly > calibration.threshold
