"""R02 sensor-relative horizontal count cells; raw evidence only."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

RANGES_M = (0.0, 10.0, 25.0, 50.0, 80.0)
SECTORS = 8
CELL_IDS = tuple(f"r{r}:a{a}" for r in range(4) for a in range(SECTORS))

@dataclass(frozen=True)
class DensityRaw:
    counts: tuple[int, ...] | None
    excluded_points: int | None
    occupied_cells: int | None
    status: str
    reason: str
    origin_id: str | None
    crop: str = "horizontal radial [0,10),[10,25),[25,50),[50,80) m; eight 45-degree sectors; all finite heights"
    units: str = "points/cell/frame"


def count_cells(xyz_native: np.ndarray | None, *, origin_xy_m: tuple[float, float] | None,
                origin_id: str | None, valid_origin: bool) -> DensityRaw:
    if not valid_origin or origin_xy_m is None or origin_id is None:
        return DensityRaw(None, None, None, "unknown", "SENSOR_ORIGIN_UNVERIFIED", origin_id)
    if xyz_native is None:
        return DensityRaw(None, None, None, "unknown", "CLOUD_UNAVAILABLE", origin_id)
    xyz = np.asarray(xyz_native)
    if xyz.ndim != 2 or xyz.shape[1] != 3 or not np.isfinite(xyz).all():
        return DensityRaw(None, None, None, "invalid", "NONFINITE_OR_BAD_XYZ", origin_id)
    delta = xyz[:, :2] - np.asarray(origin_xy_m)
    radius = np.hypot(delta[:, 0], delta[:, 1])
    radial = np.searchsorted(RANGES_M, radius, side="right") - 1
    sector = np.floor(np.mod(np.arctan2(delta[:, 1], delta[:, 0]), 2*np.pi) / (np.pi/4)).astype(int)
    inside = (radial >= 0) & (radial < 4)
    counts = np.bincount(radial[inside]*8 + sector[inside], minlength=32)
    result = tuple(int(x) for x in counts)
    return DensityRaw(result, int((~inside).sum()), sum(x > 0 for x in result), "known", "VALID", origin_id)


def occupancy_change(current: DensityRaw, previous: DensityRaw | None) -> tuple[int, ...] | None:
    if previous is None or current.counts is None or previous.counts is None:
        return None
    return tuple(int(c > 0) - int(p > 0) for c, p in zip(current.counts, previous.counts))
