"""Receiver-owned spatial regions for the operational GT-free track."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from math import isfinite

import numpy as np


@dataclass(frozen=True)
class Tile:
    """A half-open receiver-frame tile; boundaries never depend on sender data."""

    region_id: str
    lower_m: tuple[float, float, float]
    upper_m: tuple[float, float, float]

    def __post_init__(self) -> None:
        lower = np.asarray(self.lower_m, dtype=float)
        upper = np.asarray(self.upper_m, dtype=float)
        if (not self.region_id.startswith("gt_free:tile:") or lower.shape != (3,)
                or upper.shape != (3,) or not np.isfinite((lower, upper)).all()
                or not (upper > lower).all()):
            raise ValueError("invalid GT-free tile")


@dataclass(frozen=True)
class FrozenTileGrid:
    """Complete, immutable tile universe frozen before a tested cloud arrives."""

    tiles: tuple[Tile, ...]
    frozen_ns: int
    receiver_frame: str
    authority: str = "receiver"
    track: str = "gt_free"

    def __post_init__(self) -> None:
        if (self.authority, self.track) != ("receiver", "gt_free"):
            raise ValueError("GT-free regions must be receiver-owned")
        if self.frozen_ns < 0 or not self.receiver_frame or not self.tiles:
            raise ValueError("invalid frozen tile grid")
        if len({tile.region_id for tile in self.tiles}) != len(self.tiles):
            raise ValueError("duplicate tile IDs")

    @property
    def digest(self) -> str:
        payload = {
            "authority": self.authority,
            "track": self.track,
            "frozen_ns": self.frozen_ns,
            "receiver_frame": self.receiver_frame,
            "tiles": [
                {"region_id": tile.region_id, "lower_m": tile.lower_m, "upper_m": tile.upper_m}
                for tile in self.tiles
            ],
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def make_fixed_grid(*, x_limits_m: tuple[float, float], y_limits_m: tuple[float, float],
                    z_limits_m: tuple[float, float], tile_size_m: tuple[float, float],
                    frozen_ns: int, receiver_frame: str = "receiver") -> FrozenTileGrid:
    """Create the configured grid without accepting a cloud or sender claim."""
    values = (*x_limits_m, *y_limits_m, *z_limits_m, *tile_size_m)
    if not all(isfinite(value) for value in values):
        raise ValueError("grid geometry must be finite")
    if (x_limits_m[1] <= x_limits_m[0] or y_limits_m[1] <= y_limits_m[0]
            or z_limits_m[1] <= z_limits_m[0] or min(tile_size_m) <= 0):
        raise ValueError("invalid grid extents")
    nx = (x_limits_m[1] - x_limits_m[0]) / tile_size_m[0]
    ny = (y_limits_m[1] - y_limits_m[0]) / tile_size_m[1]
    if not (float(nx).is_integer() and float(ny).is_integer()):
        raise ValueError("tile size must divide the receiver ROI")
    tiles = []
    for iy in range(int(ny)):
        for ix in range(int(nx)):
            x0 = x_limits_m[0] + ix * tile_size_m[0]
            y0 = y_limits_m[0] + iy * tile_size_m[1]
            tiles.append(Tile(
                f"gt_free:tile:x{ix:02d}:y{iy:02d}",
                (x0, y0, z_limits_m[0]),
                (x0 + tile_size_m[0], y0 + tile_size_m[1], z_limits_m[1]),
            ))
    return FrozenTileGrid(tuple(tiles), frozen_ns, receiver_frame)


def count_fixed_tiles(points_m: np.ndarray, grid: FrozenTileGrid) -> tuple[dict[str, int], int]:
    """Count finite receiver-frame points; return all tile counts and outside count."""
    points = np.asarray(points_m, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
        raise ValueError("points must be finite N x 3 receiver-frame coordinates")
    counts = {tile.region_id: 0 for tile in grid.tiles}
    covered = np.zeros(len(points), dtype=bool)
    for tile in grid.tiles:
        inside = ((points >= tile.lower_m) & (points < tile.upper_m)).all(axis=1)
        counts[tile.region_id] = int(inside.sum())
        covered |= inside
    return counts, int((~covered).sum())


def receiver_context(*, receiver_range_m: float | None, range_bins_m: tuple[float, ...],
                     allow_broad_context: bool) -> tuple[str | None, str]:
    """Choose context from trusted receiver state, or an explicit broad fallback."""
    if receiver_range_m is None:
        return ("receiver_range:all", "broad_receiver_context") if allow_broad_context else (None, "RANGE_UNKNOWN")
    if not isfinite(receiver_range_m) or receiver_range_m < 0:
        raise ValueError("receiver range must be finite and nonnegative")
    if tuple(sorted(range_bins_m)) != range_bins_m or any(value <= 0 for value in range_bins_m):
        raise ValueError("range bins must be positive and increasing")
    for upper in range_bins_m:
        if receiver_range_m < upper:
            return f"receiver_range:lt_{upper:g}m", "receiver_owned_range"
    return "receiver_range:overflow", "receiver_owned_range"
