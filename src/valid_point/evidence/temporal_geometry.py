"""Causal directed geometric novelty with deterministic voxel support."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class GeometryRaw:
    distance_m: float | None
    status: str
    reason: str
    current_voxels: int | None
    previous_voxels: int | None
    gap_s: float | None
    previous_cloud_id: str | None
    current_pose_id: str | None
    previous_pose_id: str | None
    downsampled_current: int = 0
    downsampled_previous: int = 0
    approximate: bool = False
    crop: str = "horizontal radius [0,80) m; all finite heights"


def voxel_centroids(xyz: np.ndarray, origin_xy: tuple[float,float], voxel_m: float = .5,
                    cap: int = 50000) -> tuple[np.ndarray, int]:
    xyz = np.asarray(xyz, dtype=np.float64)
    radius = np.hypot(xyz[:,0]-origin_xy[0], xyz[:,1]-origin_xy[1])
    valid = xyz[radius < 80]
    if len(valid) == 0:
        return np.empty((0,3), dtype=np.float64), 0
    keys, inverse = np.unique(np.floor(valid / voxel_m).astype(np.int32), axis=0, return_inverse=True)
    counts = np.bincount(inverse)
    centers = np.column_stack([np.bincount(inverse, weights=valid[:,i]) / counts for i in range(3)])
    original = len(centers)
    if original > cap:
        # Spatially uniform deterministic selection in lexicographic voxel order.
        selection = np.linspace(0, original-1, cap, dtype=int)
        centers = centers[selection]
    return centers, original - len(centers)


def _directed_distances(current: np.ndarray, previous: np.ndarray, *, bucket_m: float = 2.0,
                        max_shell: int = 4) -> np.ndarray | None:
    """Exact within searched buckets; return None if a point needs farther search.

    The bounded 2 m bucket index searches up to four Chebyshev shells. A nearest
    point found within the inner boundary of the last searched shell is exact;
    otherwise the whole G measurement is unknown rather than capped numeric.
    """
    from collections import defaultdict
    buckets: dict[tuple[int,int,int], list[int]] = defaultdict(list)
    pk = np.floor(previous / bucket_m).astype(np.int32)
    for i, key in enumerate(pk):
        buckets[tuple(int(x) for x in key)].append(i)
    out = np.empty(len(current), dtype=np.float64)
    ck = np.floor(current / bucket_m).astype(np.int32)
    # Group current centroids by bucket to reuse neighbor lookup.
    groups: dict[tuple[int,int,int], list[int]] = defaultdict(list)
    for i, key in enumerate(ck):
        groups[tuple(int(x) for x in key)].append(i)
    for key, indexes in groups.items():
        remaining = np.asarray(indexes, dtype=int)
        best = np.full(len(remaining), np.inf)
        for shell in range(max_shell + 1):
            candidates = []
            for dx in range(-shell,shell+1):
                for dy in range(-shell,shell+1):
                    for dz in range(-shell,shell+1):
                        if max(abs(dx),abs(dy),abs(dz)) != shell:
                            continue
                        candidates.extend(buckets.get((key[0]+dx,key[1]+dy,key[2]+dz), ()))
            if candidates:
                target = previous[candidates]
                # Chunk for bounded memory; no N x N global matrix.
                for start in range(0, len(remaining), 128):
                    subset = current[remaining[start:start+128]]
                    for cstart in range(0, len(target), 256):
                        squared = ((subset[:,None,:]-target[None,cstart:cstart+256,:])**2).sum(axis=2)
                        best[start:start+len(subset)] = np.minimum(best[start:start+len(subset)], np.sqrt(squared.min(axis=1)))
            # Any point with distance <= distance to all unsearched bucket faces is final.
            low = np.asarray(key)*bucket_m
            high = low + bucket_m
            pts = current[remaining]
            boundary = np.min(np.column_stack((pts-low, high-pts)), axis=1) + shell*bucket_m
            done = best <= boundary
            out[remaining[done]] = best[done]
            remaining, best = remaining[~done], best[~done]
            if len(remaining) == 0:
                break
        if len(remaining):
            return None
    return out


def directed_novelty(current_xyz: np.ndarray | None, previous_xyz: np.ndarray | None,
                     *, current_origin_xy: tuple[float,float], previous_origin_xy: tuple[float,float],
                     map_from_current: np.ndarray | None, map_from_previous: np.ndarray | None,
                     gap_s: float | None, previous_cloud_id: str | None,
                     current_pose_id: str | None, previous_pose_id: str | None,
                     min_voxels: int = 100, max_gap_s: float = .5) -> GeometryRaw:
    def unknown(reason, nc=None, np_=None, dc=0, dp=0):
        return GeometryRaw(None,"unknown",reason,nc,np_,gap_s,previous_cloud_id,current_pose_id,previous_pose_id,dc,dp)
    if current_xyz is None or previous_xyz is None or previous_cloud_id is None:
        return unknown("NO_CAUSAL_HISTORY")
    if gap_s is None or gap_s <= 0 or gap_s > max_gap_s:
        return unknown("GAP_OUT_OF_RANGE")
    for transform in (map_from_current,map_from_previous):
        if transform is None or transform.shape != (4,4) or not np.isfinite(transform).all() or not np.allclose(transform[3], [0,0,0,1]) or not np.allclose(transform[:3,:3].T@transform[:3,:3], np.eye(3), atol=1e-3) or np.linalg.det(transform[:3,:3]) < .999:
            return unknown("INVALID_TRANSFORM")
    if not np.isfinite(current_xyz).all() or not np.isfinite(previous_xyz).all():
        return unknown("NONFINITE_XYZ")
    current, dc = voxel_centroids(current_xyz, current_origin_xy)
    previous, dp = voxel_centroids(previous_xyz, previous_origin_xy)
    if len(current) < min_voxels or len(previous) < min_voxels:
        return unknown("INSUFFICIENT_VOXEL_SUPPORT",len(current),len(previous),dc,dp)
    transform = np.linalg.inv(map_from_current) @ map_from_previous
    previous_in_current = previous @ transform[:3,:3].T + transform[:3,3]
    distances = _directed_distances(current, previous_in_current)
    if distances is None:
        return unknown("NEIGHBOR_SEARCH_BOUND",len(current),len(previous),dc,dp)
    return GeometryRaw(float(np.quantile(distances,.9)),"known","VALID",len(current),len(previous),gap_s,previous_cloud_id,current_pose_id,previous_pose_id,dc,dp,dc>0 or dp>0)
