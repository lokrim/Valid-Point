"""Bounded, label independent Mixed Signals intake primitives.

The published reader's coordinate conventions are recorded in planning/sources.md.
This module deliberately keeps source stamps, synchronization IDs and raw fields.
"""

from __future__ import annotations

import bisect
from collections import Counter
import csv
import io
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
from typing import BinaryIO

import numpy as np


STREAM_PRINCIPAL = {"003": "003", "004": "004", "laser": "laser", "top": "RSU", "dome": "RSU"}
SOURCE_RE = re.compile(r"^(003|004|laser|top|dome)_(\d+)_(\d+)\.(\d{1,9})\.pcd$")
TOP_FROM_MAP = np.array([41.551, 51.878, 1.077], dtype=np.float64)
DOME_FROM_MAP = np.array([41.507, 51.864, 1.340], dtype=np.float64)


@dataclass(frozen=True)
class CloudName:
    path: str
    stream: str
    principal: str
    sync_id: int
    stamp_text: str
    source_ns: int


def parse_stamp(seconds: str, subsecond: str) -> int:
    """Legacy devkit convention: a short subsecond is LEFT padded to ns."""
    if not seconds.isdecimal() or not subsecond.isdecimal() or not 1 <= len(subsecond) <= 9:
        raise ValueError("invalid source timestamp")
    return int(seconds) * 1_000_000_000 + int(subsecond.zfill(9))


def parse_cloud_name(path: str) -> CloudName:
    match = SOURCE_RE.fullmatch(PurePosixPath(path).name)
    if match is None:
        raise ValueError(f"unexpected cloud filename: {path}")
    stream, sync, sec, sub = match.groups()
    return CloudName(path, stream, STREAM_PRINCIPAL[stream], int(sync), f"{sec}.{sub}", parse_stamp(sec, sub))


def safe_members(archive: Path) -> list[dict]:
    """Inventory an ordinary TAR before any extraction; fail closed on unsafe types."""
    size = archive.stat().st_size
    seen: set[str] = set()
    rows: list[dict] = []
    logical = 0
    with tarfile.open(archive, "r:") as tar:
        for member in tar:
            name = member.name
            path = PurePosixPath(name)
            parts = path.parts
            if not name or name.startswith("/") or "\\" in name or any(p in ("", ".", "..") for p in parts):
                raise ValueError(f"unsafe member path: {name!r}")
            canonical = str(path)
            if canonical != name.rstrip("/") or canonical in seen:
                raise ValueError(f"duplicate/noncanonical member: {name!r}")
            seen.add(canonical)
            if not (member.isfile() or member.isdir()):
                raise ValueError(f"link or special member: {name!r}, type={member.type!r}")
            if getattr(member, "sparse", None) or any("sparse" in key.lower() for key in member.pax_headers):
                raise ValueError(f"sparse member: {name!r}")
            if member.size < 0 or (member.isfile() and member.offset_data + member.size > size):
                raise ValueError(f"invalid member extent: {name!r}")
            if member.isfile():
                logical += member.size
            rows.append({"path": canonical, "bytes": member.size, "kind": "file" if member.isfile() else "directory"})
    files = {r["path"] for r in rows if r["kind"] == "file"}
    if any(any(str(PurePosixPath(p).parent) == f or str(PurePosixPath(p).parent).startswith(f + "/") for f in files) for p in seen):
        raise ValueError("file used as parent path")
    if logical > size:
        raise ValueError("logical expansion exceeds archive size")
    return rows


def select_window(clouds: list[CloudName], seconds: int = 5, limit: int = 50) -> tuple[int, dict[str, list[CloudName]]]:
    """First source-time interval with >=2 principals; selection sees names only."""
    ordered = sorted(clouds, key=lambda c: (c.source_ns, c.stream, c.sync_id))
    width = seconds * 1_000_000_000
    for candidate in ordered:
        start = candidate.source_ns
        present = {c.principal for c in ordered if start <= c.source_ns < start + width}
        if len(present) >= 2:
            selected = {
                stream: sorted((c for c in ordered if c.stream == stream and start <= c.source_ns < start + width), key=lambda c: (c.source_ns, c.sync_id))[:limit]
                for stream in STREAM_PRINCIPAL
            }
            return start, selected
    raise ValueError("no five-second interval with two physical principals")


def id_coverage(clouds: list[CloudName]) -> tuple[dict[int, int], list[int]]:
    counts = Counter(cloud.sync_id for cloud in clouds)
    if not counts:
        return {}, []
    duplicates = {key: count for key, count in counts.items() if count > 1}
    missing = sorted(set(range(min(counts), max(counts) + 1)) - set(counts))
    return duplicates, missing


def extract_selected(archive: Path, root: Path, names: list[str], inventory: list[dict], cap: int = 2_000_000_000) -> int:
    """Copy only preapproved regular files; never invoke extractall."""
    index = {r["path"]: r for r in inventory}
    if len(names) != len(set(names)) or any(n not in index or index[n]["kind"] != "file" for n in names):
        raise ValueError("selection not contained in safe inventory")
    total = sum(index[n]["bytes"] for n in names)
    if total > cap:
        raise ValueError(f"selected extraction {total} exceeds {cap}")
    if any((root / n).exists() for n in names):
        raise FileExistsError("selected raw destination already exists")
    with tarfile.open(archive, "r:") as tar:
        for name in names:
            member = tar.getmember(name)
            if not member.isfile() or member.size != index[name]["bytes"]:
                raise ValueError(f"member changed: {name}")
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source, destination.open("xb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
            if destination.stat().st_size != member.size:
                raise IOError(f"short extraction: {name}")
            destination.chmod(0o444)
    return total


@dataclass(frozen=True)
class PCDHeader:
    raw: str
    fields: tuple[str, ...]
    sizes: tuple[int, ...]
    types: tuple[str, ...]
    counts: tuple[int, ...]
    width: int
    height: int
    points: int
    encoding: str
    byte_offset: int


def read_pcd_header(handle: BinaryIO) -> PCDHeader:
    lines: list[str] = []
    entries: dict[str, list[str]] = {}
    consumed = 0
    for _ in range(32):
        raw = handle.readline(4096)
        consumed += len(raw)
        if not raw or consumed > 32768 or not raw.endswith(b"\n"):
            raise ValueError("unterminated/oversized PCD header")
        try:
            line = raw.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ValueError("non-ASCII PCD header") from exc
        lines.append(line)
        tokens = line.strip().split()
        if not tokens or tokens[0].startswith("#"):
            continue
        key = tokens[0].upper()
        if key in entries:
            raise ValueError(f"duplicate PCD header key {key}")
        entries[key] = tokens[1:]
        if key == "DATA":
            break
    else:
        raise ValueError("missing DATA header")
    needed = ("FIELDS", "SIZE", "TYPE", "COUNT", "WIDTH", "HEIGHT", "POINTS", "DATA")
    if any(k not in entries for k in needed):
        raise ValueError("missing required PCD header key")
    fields = tuple(entries["FIELDS"])
    sizes = tuple(map(int, entries["SIZE"]))
    types = tuple(entries["TYPE"])
    counts = tuple(map(int, entries["COUNT"]))
    width, height, points = (int(entries[k][0]) for k in ("WIDTH", "HEIGHT", "POINTS"))
    if not fields or len(set(fields)) != len(fields) or not len(fields) == len(sizes) == len(types) == len(counts):
        raise ValueError("invalid PCD field vectors")
    if any(s not in (1, 2, 4, 8) for s in sizes) or any(t not in ("F", "I", "U") for t in types) or any(c <= 0 for c in counts):
        raise ValueError("invalid PCD field type")
    if width <= 0 or height <= 0 or points != width * height or points > 10_000_000:
        raise ValueError("invalid PCD dimensions")
    if len(entries["DATA"]) != 1:
        raise ValueError("invalid DATA declaration")
    return PCDHeader("".join(lines), fields, sizes, types, counts, width, height, points, entries["DATA"][0].lower(), consumed)


def read_pcd(handle: BinaryIO) -> tuple[PCDHeader, np.ndarray]:
    header = read_pcd_header(handle)
    if header.encoding != "ascii":
        raise ValueError(f"unsupported PCD encoding: {header.encoding}")
    if any(t != "F" or s != 4 or c != 1 for t, s, c in zip(header.types, header.sizes, header.counts)):
        raise ValueError("unsupported PCD field layout")
    if not {"x", "y", "z"}.issubset(header.fields):
        raise ValueError("missing XYZ")
    body = handle.read()
    values = np.fromstring(body.decode("ascii"), sep=" ", dtype=np.float32)
    if values.size != header.points * len(header.fields):
        raise ValueError(f"PCD body count {values.size} != {header.points * len(header.fields)}")
    return header, values.reshape(header.points, len(header.fields))


def load_odometry(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("missing or duplicate CSV columns")
        rows = list(reader)
    return list(reader.fieldnames), rows


def pose_matrix(position: tuple[float, float, float], quaternion_wxyz: tuple[float, float, float, float]) -> np.ndarray:
    w, x, y, z = map(float, quaternion_wxyz)
    norm = w*w + x*x + y*y + z*z
    if not np.isfinite(norm) or abs(norm - 1.0) > 0.02:
        raise ValueError("invalid quaternion norm")
    w, x, y, z = np.array([w, x, y, z]) / np.sqrt(norm)
    mat = np.eye(4, dtype=np.float64)
    mat[:3, :3] = [
        [1 - 2*(y*y + z*z), 2*(x*y - w*z), 2*(x*z + w*y)],
        [2*(x*y + w*z), 1 - 2*(x*x + z*z), 2*(y*z - w*x)],
        [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x*x + y*y)],
    ]
    mat[:3, 3] = position
    if not np.isfinite(mat).all():
        raise ValueError("nonfinite pose")
    return mat


def latest_past(stamps: list[int], query_ns: int) -> int | None:
    index = bisect.bisect_right(stamps, query_ns) - 1
    return index if index >= 0 else None


def nearest_reference(stamps: list[int], query_ns: int) -> int | None:
    if not stamps:
        return None
    return min(range(len(stamps)), key=lambda i: abs(stamps[i] - query_ns))


def optional_twist(row: dict[str, str]) -> tuple[float, float, float] | None:
    """Expose present linear twist values without assigning measurement provenance."""
    keys = [f"field.twist.twist.linear.{axis}" for axis in "xyz"]
    if any(not row.get(key) for key in keys):
        return None
    try:
        result = tuple(float(row[key]) for key in keys)
    except ValueError:
        return None
    return result if np.isfinite(result).all() else None


def transform_xyz(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    return points @ matrix[:3, :3].T + matrix[:3, 3]


def raw_to_top(stream: str, pose_map_from_vehicle: np.ndarray | None = None) -> np.ndarray | None:
    result = np.eye(4)
    if stream in ("top", "dome"):
        # Both raw RSU PCDs are map coordinates in the pinned reader.
        result[:3, 3] = TOP_FROM_MAP
        return result
    if pose_map_from_vehicle is None:
        return None
    # PCD z -3.25 and pose right-composed +3.25 cancel exactly.
    result[:3, 3] = TOP_FROM_MAP
    return result @ pose_map_from_vehicle
