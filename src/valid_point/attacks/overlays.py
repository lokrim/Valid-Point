"""Point-only overlays. Selection uses immutable row IDs and a frame key."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import numpy as np

from valid_point.evidence.density import CELL_IDS, RANGES_M

SEED = 20261008
FAMILIES = ("random_removal", "localized_removal", "displacement", "rearrangement", "addition")
MIDDLE = {"random_removal": .3, "localized_removal": .5,
          "displacement": 1., "rearrangement": 1., "addition": .05}


def seed_key(segment: str, principal: str, filename: str, family: str,
             severity: float, replicate: int = SEED) -> str:
    if family not in FAMILIES or severity < 0:
        raise ValueError("invalid overlay key")
    return sha256("\x1f".join(map(str, (segment, principal, filename, family,
                                           format(severity, ".12g"), replicate))).encode()).hexdigest()


def selected_ids(n: int, fraction: float, key: str) -> np.ndarray:
    if n < 0 or not 0 <= fraction <= 1:
        raise ValueError("invalid selection")
    k = int(np.floor(fraction*n))
    rng = np.random.default_rng(int(key[:16], 16))
    return np.sort(rng.choice(n, size=k, replace=False))


def cell_index(xyz: np.ndarray, origin_xy: tuple[float, float]) -> np.ndarray:
    delta = np.asarray(xyz)[:, :2] - np.asarray(origin_xy)
    radius = np.hypot(delta[:, 0], delta[:, 1])
    radial = np.searchsorted(RANGES_M, radius, side="right") - 1
    sector = np.floor(np.mod(np.arctan2(delta[:, 1], delta[:, 0]), 2*np.pi)/(np.pi/4)).astype(int)
    return np.where((radial >= 0) & (radial < 4), radial*8 + sector, -1)


@dataclass(frozen=True)
class Target:
    cell_id: str | None
    center_xyz_m: tuple[float, float, float] | None
    prefix_cloud_ids: tuple[str, ...]
    prefix_point_count: int


def freeze_target(prefix: list[tuple[str, np.ndarray]], *, origin_xy=(0., 0.)) -> Target:
    """Choose the most occupied valid D cell using sender-only first 3 s."""
    counts = np.zeros(32, dtype=np.int64)
    sums = np.zeros((32, 3), dtype=np.float64)
    for _, cloud in prefix:
        cells = cell_index(cloud[:, :3], origin_xy)
        valid = cells >= 0
        counts += np.bincount(cells[valid], minlength=32)
        for axis in range(3):
            sums[:, axis] += np.bincount(cells[valid], weights=cloud[valid, axis], minlength=32)
    if not counts.any():
        return Target(None, None, tuple(x[0] for x in prefix), 0)
    selected = int(np.argmax(counts))
    return Target(CELL_IDS[selected], tuple((sums[selected]/counts[selected]).tolist()),
                  tuple(x[0] for x in prefix), int(counts[selected]))


@dataclass(frozen=True)
class OverlayResult:
    values: np.ndarray
    selected_ids: tuple[int, ...]
    changed_ids: tuple[int, ...]
    failed_ids: tuple[int, ...]
    added: int
    intended_count: int
    reason: str


def apply_overlay(values: np.ndarray, *, family: str, severity: float, key: str,
                  target: Target | None = None, origin_xy=(0., 0.)) -> OverlayResult:
    array = np.asarray(values, dtype=np.float32)
    if family not in FAMILIES or array.ndim != 2 or array.shape[1] != 4 or not np.isfinite(array).all():
        raise ValueError("invalid overlay input")
    if severity < 0 or (family in ("random_removal", "localized_removal", "addition") and severity > 1):
        raise ValueError("invalid overlay severity")
    n = len(array)
    if severity == 0:
        return OverlayResult(array.copy(), (), (), (), 0, 0, "IDENTITY")
    rng = np.random.default_rng(int(key[:16], 16))
    if family == "random_removal":
        ids = selected_ids(n, severity, key)
        keep = np.ones(n, dtype=bool); keep[ids] = False
        return OverlayResult(array[keep].copy(), tuple(ids.tolist()), tuple(ids.tolist()), (), 0, len(ids), "VALID" if len(ids) else "ZERO_REALIZED")
    if family == "localized_removal":
        if target is None or target.cell_id is None:
            return OverlayResult(array.copy(), (), (), (), 0, 0, "NO_TARGET")
        candidates = np.flatnonzero(cell_index(array[:, :3], origin_xy) == CELL_IDS.index(target.cell_id))
        local = selected_ids(len(candidates), severity, key)
        ids = np.sort(candidates[local]); keep = np.ones(n, dtype=bool); keep[ids] = False
        return OverlayResult(array[keep].copy(), tuple(ids.tolist()), tuple(ids.tolist()), (), 0, len(ids), "VALID" if len(ids) else "ZERO_TARGET_ROWS")
    if family == "addition":
        count = int(np.floor(severity*n))
        if target is None or target.center_xyz_m is None or not count:
            return OverlayResult(array.copy(), (), (), (), 0, count, "NO_CENTER_OR_ROWS")
        xyz = np.asarray(target.center_xyz_m) + rng.uniform(-1., 1., size=(count, 3))
        intensity = array[rng.choice(n, size=count), 3] if n else np.zeros(count)
        added = np.column_stack((xyz, intensity)).astype(np.float32)
        return OverlayResult(np.concatenate((array, added)), (), tuple(range(n, n+count)), (), count, count, "VALID")
    ids = selected_ids(n, .25, key)
    changed = array.copy()
    if family == "displacement":
        changed[ids, 0] += np.float32(severity)
        moved = ids[np.any(changed[ids, :3] != array[ids, :3], axis=1)]
        return OverlayResult(changed, tuple(ids.tolist()), tuple(moved.tolist()), tuple(np.setdiff1d(ids,moved).tolist()), 0, len(ids), "VALID" if len(moved) else "ZERO_REALIZED")
    original_cells = cell_index(array[:, :3], origin_xy)
    remaining = ids.copy()
    moved_parts=[]
    # Frozen proposal budget; direction order depends on the per-frame key only.
    angles = np.arange(10)*2*np.pi/10 + rng.uniform(0, 2*np.pi)
    for angle in angles:
        if not len(remaining):
            break
        proposal = changed[remaining, :3].copy()
        proposal[:, 0] += severity*np.cos(angle)
        proposal[:, 1] += severity*np.sin(angle)
        valid = (original_cells[remaining] >= 0) & (cell_index(proposal, origin_xy) == original_cells[remaining])
        valid_ids=remaining[valid]
        changed[valid_ids, :3] = proposal[valid]
        moved_parts.append(valid_ids)
        remaining=remaining[~valid]
    moved = np.sort(np.concatenate(moved_parts)) if moved_parts else np.empty(0, dtype=int)
    return OverlayResult(changed, tuple(ids.tolist()), tuple(moved.tolist()), tuple(remaining.tolist()), 0, len(ids), "VALID" if len(moved) else "NO_VALID_PROPOSAL")
