"""R02 operational, label-independent event ingestion and causal raw factors.

Only allowlisted cloud and odometry paths are read. This module accepts neither
labels nor evaluator state. Arrival=source is a declared replay assumption.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
import csv
import hashlib
import time
import numpy as np

from valid_point.io.mixed_signals import (CloudName, STREAM_PRINCIPAL, DOME_FROM_MAP,
    TOP_FROM_MAP, parse_cloud_name, pose_matrix, read_pcd)
from valid_point.evidence.density import DensityRaw, count_cells, occupancy_change
from valid_point.evidence.temporal_geometry import GeometryRaw, directed_novelty

VEHICLES = ("003", "004", "laser")
POSE_COLUMNS = tuple(f"field.pose.pose.position.{x}" for x in "xyz") + tuple(f"field.pose.pose.orientation.{x}" for x in "wxyz")

@dataclass(frozen=True)
class ReplayConfig:
    max_pose_age_ns: int = 150_000_000
    max_cloud_age_ns: int = 150_000_000
    max_gap_s: float = .5
    min_voxels: int = 100
    receipt_model: str = "ideal_arrival_equals_source; modeled receiver pose availability equals pose stamp"
    factor_version: str = "R02.raw.v1"
    validated_origins: tuple[str, ...] = tuple(STREAM_PRINCIPAL)

@dataclass(frozen=True)
class CloudEvent:
    cloud_id: str
    stream: str
    principal: str
    sync_id: int
    source_ns: int
    arrival_ns: int
    deadline_ns: int
    path: Path | None
    state: str = "present"

    def __post_init__(self):
        if self.stream not in STREAM_PRINCIPAL or self.principal != STREAM_PRINCIPAL[self.stream]:
            raise ValueError("invalid stream/principal mapping")
        if self.state not in ("present", "absent") or (self.path is None) != (self.state == "absent"):
            raise ValueError("invalid cloud state/path")
        if any(type(x) is not int for x in (self.sync_id,self.source_ns,self.arrival_ns,self.deadline_ns)):
            raise ValueError("timestamps and index must be integers")

@dataclass(frozen=True)
class PoseEvent:
    pose_id: str
    stream: str
    source_ns: int
    available_ns: int
    matrix: np.ndarray | None
    valid: bool

@dataclass(frozen=True)
class RawFactorRecord:
    cloud_id: str
    stream: str
    principal: str
    sync_id: int
    source_ns: int
    arrival_ns: int
    deadline_ns: int
    state: str
    input_sha256: str | None
    pose_id: str | None
    pose_age_s: float | None
    history_id: str | None
    history_pose_id: str | None
    density: DensityRaw
    geometry: GeometryRaw
    occupancy_change: tuple[int, ...] | None
    reason: str

    def as_dict(self) -> dict:
        return asdict(self)

class AllowedSource:
    """Filesystem boundary. Discovery and reads stay inside explicit raw dirs."""
    def __init__(self, clouds_dir: Path, poses_dir: Path):
        self.clouds_dir = clouds_dir.resolve(strict=True)
        self.poses_dir = poses_dir.resolve(strict=True)
        self.access_log: list[str] = []

    def _check(self, path: Path, parent: Path) -> Path:
        resolved = path.resolve(strict=True)
        if resolved.parent != parent or not resolved.is_file():
            raise PermissionError(f"input outside operational allowlist: {path}")
        return resolved

    def cloud_names(self, *, max_sync_id: int = 299, first_seconds: float = 30.) -> list[CloudName]:
        if max_sync_id < 0 or max_sync_id > 299 or first_seconds <= 0 or first_seconds > 30:
            raise ValueError("R02 bound exceeds first 30 seconds / 300 indices")
        names = []
        for path in self.clouds_dir.glob("*.pcd"):
            item = parse_cloud_name(path.name)
            if item.sync_id <= max_sync_id:
                names.append(item)
        if not names:
            return []
        start = min(x.source_ns for x in names)
        return sorted((x for x in names if x.source_ns-start < first_seconds*1e9),
                      key=lambda x: (x.source_ns,x.stream,x.sync_id))

    def events(self, *, max_sync_id: int = 299, first_seconds: float = 30.) -> list[CloudEvent]:
        return [CloudEvent(n.path,n.stream,n.principal,n.sync_id,n.source_ns,n.source_ns,n.source_ns,
                           self.clouds_dir/n.path) for n in self.cloud_names(max_sync_id=max_sync_id,first_seconds=first_seconds)]

    def read_cloud(self, event: CloudEvent) -> tuple[np.ndarray, str]:
        if event.path is None:
            raise ValueError("absent cloud")
        path = self._check(event.path,self.clouds_dir)
        name = parse_cloud_name(path.name)
        if (name.path,name.stream,name.sync_id,name.source_ns) != (event.cloud_id,event.stream,event.sync_id,event.source_ns):
            raise ValueError("cloud event/path identity mismatch")
        self.access_log.append(str(path))
        data = path.read_bytes()
        from io import BytesIO
        header, values = read_pcd(BytesIO(data))
        xyz = values[:,[header.fields.index(x) for x in "xyz"]].astype(np.float64)
        if not np.isfinite(xyz).all():
            raise ValueError("nonfinite cloud XYZ")
        return xyz, hashlib.sha256(data).hexdigest()

    def read_poses(self, stream: str) -> list[PoseEvent]:
        if stream not in VEHICLES:
            return []
        path = self._check(self.poses_dir/f"odometry_{stream}.csv",self.poses_dir)
        self.access_log.append(str(path))
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        poses=[]
        for index,row in enumerate(rows):
            stamp=int(row["field.header.stamp"])
            try:
                matrix=pose_matrix(tuple(float(row[c]) for c in POSE_COLUMNS[:3]),
                                   tuple(float(row[c]) for c in POSE_COLUMNS[3:]))
                valid=True
            except (ValueError,TypeError):
                matrix=None; valid=False
            poses.append(PoseEvent(f"{stream}:pose:{index}:{stamp}",stream,stamp,stamp,matrix,valid))
        return sorted(poses,key=lambda p:(p.source_ns,p.pose_id))


def _select_pose(poses: list[PoseEvent], source_ns: int, deadline_ns: int,
                 max_age_ns: int) -> tuple[PoseEvent | None,str]:
    eligible=[p for p in poses if p.source_ns <= source_ns and p.available_ns <= deadline_ns]
    if not eligible:
        return None,"NO_CAUSAL_POSE"
    pose=max(eligible,key=lambda p:(p.source_ns,p.pose_id))
    if source_ns-pose.source_ns > max_age_ns:
        return None,"STALE_POSE"
    if not pose.valid or pose.matrix is None:
        return None,"INVALID_POSE"
    return pose,"VALID"


def _frame(stream: str, pose: PoseEvent | None) -> tuple[np.ndarray | None,tuple[float,float] | None,str | None]:
    if stream == "top":
        # Released RSU raw XYZ are already in map coordinates.
        mat=np.eye(4)
        return mat,(float(-TOP_FROM_MAP[0]),float(-TOP_FROM_MAP[1])),"top:published_map_origin"
    if stream == "dome":
        mat=np.eye(4)
        return mat,(float(-DOME_FROM_MAP[0]),float(-DOME_FROM_MAP[1])),"dome:published_map_origin"
    if pose is None or pose.matrix is None:
        return None,(0.,0.),f"{stream}:native_xy_origin"
    # Raw vehicle XY is relative to its own origin. Paired z shifts cancel in
    # the published reader's raw-to-map convention; radial XY is unaffected.
    return pose.matrix,(0.,0.),f"{stream}:native_xy_origin"


def replay(events: Iterable[CloudEvent], source: AllowedSource, *, config: ReplayConfig = ReplayConfig(),
           poses: dict[str,list[PoseEvent]] | None = None) -> tuple[RawFactorRecord,...]:
    event_list=list(events)
    if poses is None:
        poses={stream:source.read_poses(stream) for stream in VEHICLES}
    history: dict[str,tuple[CloudEvent,np.ndarray,np.ndarray,tuple[float,float],str | None,DensityRaw]]={}
    output=[]
    for event in event_list:
        pose=None; pose_reason="STATIC_RSU"
        if event.stream in VEHICLES:
            pose,pose_reason=_select_pose(poses.get(event.stream,[]),event.source_ns,event.deadline_ns,config.max_pose_age_ns)
        transform,origin,origin_id=_frame(event.stream,pose)
        if event.stream not in config.validated_origins:
            origin,origin_id=None,None
        prior=history.get(event.stream)
        xyz=None; digest=None; reason="VALID"
        if event.state == "absent":
            reason="CLOUD_ABSENT"
        elif event.source_ns > event.deadline_ns:
            reason="FUTURE_SOURCE"
        elif event.arrival_ns > event.deadline_ns:
            reason="LATE_ARRIVAL"
        elif event.arrival_ns < event.source_ns:
            reason="ARRIVAL_BEFORE_SOURCE"
        elif event.deadline_ns-event.source_ns > config.max_cloud_age_ns:
            reason="STALE_CLOUD"
        else:
            try:
                xyz,digest=source.read_cloud(event)
            except (ValueError,OSError,PermissionError,UnicodeError) as exc:
                reason="MALFORMED_OR_FORBIDDEN_CLOUD:"+type(exc).__name__
        if reason != "VALID":
            density=DensityRaw(None,None,None,"unknown",reason,origin_id)
        else:
            density=count_cells(xyz,origin_xy_m=origin,origin_id=origin_id,valid_origin=origin is not None)
        if reason != "VALID":
            g_reason=reason
        elif origin is None:
            g_reason="SENSOR_ORIGIN_UNVERIFIED"
        elif transform is None:
            g_reason=pose_reason
        elif prior is None:
            g_reason="NO_CAUSAL_HISTORY"
        else:
            g_reason="VALID"
        if g_reason == "VALID" and prior is not None:
            old_event,old_xyz,old_transform,old_origin,old_pose_id,old_density=prior
            geometry=directed_novelty(xyz,old_xyz,current_origin_xy=origin,previous_origin_xy=old_origin,
                map_from_current=transform,map_from_previous=old_transform,
                gap_s=(event.source_ns-old_event.source_ns)/1e9,previous_cloud_id=old_event.cloud_id,
                current_pose_id=pose.pose_id if pose else None,previous_pose_id=old_pose_id,
                min_voxels=config.min_voxels,max_gap_s=config.max_gap_s)
        else:
            geometry=GeometryRaw(None,"unknown",g_reason,None,None,None,
                prior[0].cloud_id if prior else None,pose.pose_id if pose else None,
                prior[4] if prior else None)
        delta=occupancy_change(density,prior[5] if prior else None)
        output.append(RawFactorRecord(event.cloud_id,event.stream,event.principal,event.sync_id,
            event.source_ns,event.arrival_ns,event.deadline_ns,event.state,digest,
            pose.pose_id if pose else None,(event.source_ns-pose.source_ns)/1e9 if pose else None,
            prior[0].cloud_id if prior else None,prior[4] if prior else None,density,geometry,delta,
            reason if reason != "VALID" else pose_reason if transform is None else "VALID"))
        # The most recent eligible cloud, even if geometrically unusual, becomes history.
        if reason == "VALID" and transform is not None and origin is not None and (prior is None or event.source_ns > prior[0].source_ns):
            history[event.stream]=(event,xyz,transform,origin,pose.pose_id if pose else None,density)
    return tuple(output)
