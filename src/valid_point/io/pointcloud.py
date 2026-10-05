"""Strict JSON interchange for S01 synthetic clouds, using the later overlay reader."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np


FIELDS = ("x_m", "y_m", "z_m", "intensity")
SCHEMA = "valid_point.synthetic_cloud.v1"


@dataclass(frozen=True)
class PointCloud:
    frame: str
    points: tuple[tuple[float, float, float, float], ...]
    fields: tuple[str, ...] = FIELDS

    def __post_init__(self) -> None:
        if not self.frame or self.fields != FIELDS:
            raise ValueError("unsupported frame or point fields")
        array = np.asarray(self.points, dtype=float)
        if array.size == 0:
            array = array.reshape(0, 4)
        if array.ndim != 2 or array.shape[1] != 4 or not np.isfinite(array).all():
            raise ValueError("points must be finite rows of x/y/z/intensity")
        if any(not isinstance(row, (tuple, list)) or len(row) != 4 for row in self.points):
            raise ValueError("point row width differs")

    @property
    def count(self) -> int:
        return len(self.points)

    def xyz(self) -> np.ndarray:
        return np.asarray([row[:3] for row in self.points], dtype=float).reshape(-1, 3)


def write_pointcloud(path: Path, cloud: PointCloud) -> None:
    payload = {"schema": SCHEMA, "frame": cloud.frame, "fields": list(cloud.fields),
               "count": cloud.count, "points": [list(row) for row in cloud.points]}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, sort_keys=True, separators=(",", ":"), allow_nan=False)
        stream.write("\n")


def read_pointcloud(path: Path) -> PointCloud:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != {"schema", "frame", "fields", "count", "points"}:
        raise ValueError("invalid cloud schema fields")
    if value["schema"] != SCHEMA or value["fields"] != list(FIELDS) or type(value["count"]) is not int:
        raise ValueError("invalid cloud schema, fields, or count")
    if not isinstance(value["points"], list) or value["count"] != len(value["points"]):
        raise ValueError("declared count differs from points")
    cloud = PointCloud(frame=value["frame"], points=tuple(tuple(row) for row in value["points"]))
    return cloud
