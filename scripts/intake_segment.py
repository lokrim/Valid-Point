"""Execute R01 only: bounded local mini_7 schema/timing/geometry intake."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

import numpy as np

from valid_point.io.mixed_signals import (
    STREAM_PRINCIPAL, TOP_FROM_MAP, DOME_FROM_MAP, extract_selected,
    id_coverage, latest_past, load_odometry, nearest_reference, parse_cloud_name,
    pose_matrix, raw_to_top, read_pcd, read_pcd_header, safe_members,
    select_window, transform_xyz,
)


ROOT = Path(__file__).resolve().parents[1]
STAMP = "field.header.stamp"
POS = "field.pose.pose.position."
QUAT = "field.pose.pose.orientation."


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def csv_diagnostics(columns: list[str], rows: list[dict[str, str]]) -> dict:
    result = {}
    for col in columns:
        values = [r.get(col, "") for r in rows]
        nonempty = [v for v in values if v not in ("", "nan", "NaN")]
        numbers = []
        for value in nonempty:
            try:
                numbers.append(float(value))
            except ValueError:
                pass
        finite = [v for v in numbers if np.isfinite(v)]
        result[col] = {
            "missing": len(values) - len(nonempty),
            "numeric": len(numbers),
            "finite": len(finite),
            "distinct": len(set(nonempty)),
            "constant": len(set(nonempty)) <= 1 if nonempty else None,
            "min": min(finite) if finite else None,
            "max": max(finite) if finite else None,
        }
    return result


def odometry_records(path: Path) -> tuple[dict, list[tuple[int, np.ndarray]]]:
    columns, rows = load_odometry(path)
    required = [STAMP] + [POS + axis for axis in "xyz"] + [QUAT + axis for axis in "wxyz"]
    missing = sorted(set(required) - set(columns))
    poses = []
    errors = []
    quat_norms = []
    for i, row in enumerate(rows):
        if missing:
            break
        try:
            stamp = int(row[STAMP])
            position = tuple(float(row[POS + axis]) for axis in "xyz")
            quaternion = tuple(float(row[QUAT + axis]) for axis in "wxyz")
            quat_norms.append(float(np.linalg.norm(quaternion)))
            poses.append((stamp, pose_matrix(position, quaternion)))
        except (ValueError, KeyError) as exc:
            errors.append({"row": i, "error": str(exc)})
    poses.sort(key=lambda item: item[0])
    stamps = [x[0] for x in poses]
    gaps = np.diff(np.array(stamps, dtype=np.int64)) if len(stamps) > 1 else np.array([])
    small_sample_cols = [c for c in columns if c in (STAMP, "%time") or c.startswith(POS) or c.startswith(QUAT) or c.startswith("field.twist.twist.")]
    info = {
        "file": str(path.relative_to(ROOT)), "columns": columns, "row_count": len(rows),
        "required_missing": missing, "invalid_rows": errors[:20],
        "stamp_min_ns": min(stamps) if stamps else None,
        "stamp_max_ns": max(stamps) if stamps else None,
        "duplicate_stamps": len(stamps) - len(set(stamps)),
        "gap_ns": {"min": int(gaps.min()), "median": int(np.median(gaps)), "max": int(gaps.max())} if gaps.size else None,
        "quaternion_norm": {"min": min(quat_norms), "max": max(quat_norms)} if quat_norms else None,
        "sample_rows": [{c: rows[i][c] for c in small_sample_cols} for i in sorted({0, len(rows)//2, len(rows)-1})] if rows else [],
        "column_diagnostics": csv_diagnostics(columns, rows),
    }
    return info, poses


def per_stream_name_diagnostics(clouds: list) -> dict:
    ids = [c.sync_id for c in clouds]
    duplicate_ids, missing_ids = id_coverage(clouds)
    by_source = Counter(c.source_ns for c in clouds)
    ordered = sorted(clouds, key=lambda c: c.sync_id)
    jumps = [ordered[i].source_ns - ordered[i-1].source_ns for i in range(1, len(ordered))]
    gaps = [int(v) for v in jumps if v > 0]
    return {
        "count": len(clouds), "id_min": min(ids) if ids else None, "id_max": max(ids) if ids else None,
        "duplicate_ids": {str(k): v for k, v in duplicate_ids.items()},
        "missing_ids": missing_ids,
        "duplicate_source_ns": {str(k): v for k, v in by_source.items() if v > 1},
        "source_reversals_in_id_order": sum(j < 0 for j in jumps),
        "positive_id_order_gap_ns": {"min": min(gaps), "median": int(np.median(gaps)), "max": max(gaps)} if gaps else None,
        "short_subsecond_count": sum(len(c.stamp_text.split(".")[1]) < 9 for c in clouds),
    }


def make_figure(path: Path, samples: dict, metadata: dict, poses: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    fig, axes = plt.subplots(2, 2, figsize=(17, 10))
    colors = {"003": "#d62728", "004": "#2ca02c", "laser": "#9467bd", "top": "#1f77b4", "dome": "#ff7f0e"}
    for stream, xyz in samples.items():
        if xyz.size == 0:
            continue
        item = metadata[stream]
        age = item["pose_age_ms"]
        age_label = "static" if age is None else f"pose age {age:.1f} ms"
        label = f"{stream} / {item['stamp_text']} / {age_label}"
        transform = item["transform"]
        mapped = transform_xyz(xyz, np.asarray(transform)) if transform is not None else None
        for ax, xx, yy in ((axes[0, 0], xyz[:, 0], xyz[:, 1]), (axes[1, 0], xyz[:, 0], xyz[:, 2])):
            ax.scatter(xx, yy, s=0.12, alpha=0.23, color=colors[stream], rasterized=True, label=label)
        if mapped is not None:
            for ax, xx, yy in ((axes[0, 1], mapped[:, 0], mapped[:, 1]), (axes[1, 1], mapped[:, 0], mapped[:, 2])):
                ax.scatter(xx, yy, s=0.12, alpha=0.23, color=colors[stream], rasterized=True, label=label)
    for stream, matrix in poses.items():
        if matrix is None or stream in ("top", "dome"):
            continue
        point = transform_xyz(np.zeros((1, 3)), np.asarray(matrix))[0]
        axes[0, 1].scatter(point[0], point[1], marker="x", s=55, color=colors[stream])
        axes[1, 1].scatter(point[0], point[2], marker="x", s=55, color=colors[stream])
    # Origins in the TOP frame, not translations of map into sensor frames.
    dome_origin_top = TOP_FROM_MAP - DOME_FROM_MAP
    axes[0, 1].scatter(0, 0, marker="*", s=150, color=colors["top"])
    axes[0, 1].scatter(dome_origin_top[0], dome_origin_top[1], marker="*", s=150, color=colors["dome"])
    axes[1, 1].scatter(0, 0, marker="*", s=150, color=colors["top"])
    axes[1, 1].scatter(dome_origin_top[0], dome_origin_top[2], marker="*", s=150, color=colors["dome"])
    titles = (("Native raw plan (mixed source frames)", "Top-frame plan"), ("Native raw elevation (mixed source frames)", "Top-frame elevation"))
    for row in range(2):
        for col in range(2):
            ax = axes[row, col]
            ax.set_title(titles[row][col])
            ax.set_xlabel("x (m)")
            ax.set_ylabel("y (m)" if row == 0 else "z (m)")
            ax.set_aspect("equal", adjustable="datalim")
            ax.grid(alpha=0.2)
    handles, labels = axes[0, 1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center left", bbox_to_anchor=(0.76, 0.5), fontsize=9, markerscale=8)
    fig.suptitle("R01 mini_7: first selected cloud per stream; stars = RSU origins, x = vehicle poses")
    fig.tight_layout(rect=(0, 0, 0.76, 0.95))
    fig.savefig(path, dpi=180)
    plt.close(fig)


def run() -> Path:
    config_path = ROOT / "configs/development_intake.json"
    config = json.loads(config_path.read_text())
    archive = ROOT / config["archive"]
    if archive.stat().st_size != config["archive_bytes"] or digest(archive) != config["archive_sha256"]:
        raise RuntimeError("archive size/hash verification failed")
    inventory = safe_members(archive)
    index = {r["path"]: r for r in inventory}
    clouds = [parse_cloud_name(r["path"]) for r in inventory if r["path"].startswith("PointClouds/mini_7/") and r["path"].endswith(".pcd")]
    start, selected = select_window(clouds, config["window_seconds"], config["max_clouds_per_stream"])
    cloud_names = [c.path for group in selected.values() for c in group]
    odometry_names = [f"Odometry/mini_7/odometry_{s}.csv" for s in ("003", "004", "laser") if f"Odometry/mini_7/odometry_{s}.csv" in index]
    selected_names = cloud_names + odometry_names
    total = sum(index[n]["bytes"] for n in selected_names)
    if len(cloud_names) > config["max_cloud_bodies"] or total > config["max_extraction_bytes"]:
        raise RuntimeError("selection exceeds resource cap")
    free = os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize
    if free < total + 2_000_000_000:
        raise RuntimeError("insufficient extraction and output reserve")
    release = ROOT / "data/mixed_signals" / config["revision"]
    raw = release / "raw"
    if any((raw / n).exists() for n in selected_names):
        # Only immutable, exact-size prior selected files may be reused.
        if not all((raw / n).is_file() and (raw / n).stat().st_size == index[n]["bytes"] for n in selected_names):
            raise RuntimeError("partial or mismatched prior raw extraction")
        extracted = 0
    else:
        extracted = extract_selected(archive, raw, selected_names, inventory, config["max_extraction_bytes"])
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-R01"
    output = ROOT / "artifacts" / run_id
    output.mkdir(parents=True, exist_ok=False)
    log = [f"archive verified sha256={config['archive_sha256']}", f"safe members={len(inventory)}", f"selected bytes={total}; newly extracted={extracted}; free pre-extraction={free}"]
    write_json(output / "safe_member_inventory.json", inventory)
    by_stream = {s: [c for c in clouds if c.stream == s] for s in STREAM_PRINCIPAL}
    name_diagnostics = {s: per_stream_name_diagnostics(v) for s, v in by_stream.items()}
    labels = [r["path"] for r in inventory if r["path"].startswith("labels/") and r["kind"] == "file"]
    headers = {}
    with __import__("tarfile").open(archive, "r:") as tar:
        for stream, group in by_stream.items():
            ordered = sorted(group, key=lambda c: (c.source_ns, c.sync_id))
            for c in (ordered[0], ordered[len(ordered)//2], ordered[-1]) if ordered else ():
                with tar.extractfile(c.path) as source:
                    h = read_pcd_header(source)
                headers[c.path] = {"raw": h.raw, "fields": h.fields, "sizes": h.sizes, "types": h.types, "counts": h.counts, "width": h.width, "height": h.height, "points": h.points, "encoding": h.encoding}
    odometry = {}
    pose_rows = {}
    for name in odometry_names:
        stream = Path(name).stem.removeprefix("odometry_")
        info, poses = odometry_records(raw / name)
        odometry[stream] = info
        pose_rows[stream] = poses
    timing_rows = []
    geometry_samples = {}
    repeat_samples = {}
    figure_metadata = {}
    origins = {}
    stream_stats = {}
    for stream, group in selected.items():
        stats = {"cloud_count": 0, "point_count": 0, "nonfinite_xyz": 0, "nonfinite_intensity": 0, "intensity_min": None, "intensity_max": None, "encodings": {}, "observed_fields": []}
        for i, cloud in enumerate(group):
            pose = pose_rows.get(stream, [])
            stamps = [p[0] for p in pose]
            causal = latest_past(stamps, cloud.source_ns)
            nearest = nearest_reference(stamps, cloud.source_ns)
            age = cloud.source_ns - stamps[causal] if causal is not None else None
            future_reference = nearest is not None and stamps[nearest] > cloud.source_ns
            matrix = raw_to_top(stream, pose[causal][1] if causal is not None else None)
            timing_rows.append({"stream": stream, "principal": STREAM_PRINCIPAL[stream], "sync_id": cloud.sync_id, "source_text": cloud.stamp_text, "source_ns": cloud.source_ns, "pose_ns": stamps[causal] if causal is not None else None, "pose_age_ns": age, "reference_nearest_ns": stamps[nearest] if nearest is not None else None, "reference_uses_future": future_reference, "reference_differs": nearest != causal})
            with (raw / cloud.path).open("rb") as source:
                header, values = read_pcd(source)
            stats["cloud_count"] += 1
            stats["point_count"] += len(values)
            stats["encodings"][header.encoding] = stats["encodings"].get(header.encoding, 0) + 1
            stats["observed_fields"] = list(header.fields)
            xyz = values[:, [header.fields.index(s) for s in "xyz"]]
            stats["nonfinite_xyz"] += int((~np.isfinite(xyz)).any(axis=1).sum())
            if "intensity" in header.fields:
                intensity = values[:, header.fields.index("intensity")]
                valid = intensity[np.isfinite(intensity)]
                stats["nonfinite_intensity"] += len(intensity) - len(valid)
                if len(valid):
                    mn, mx = float(valid.min()), float(valid.max())
                    stats["intensity_min"] = mn if stats["intensity_min"] is None else min(mn, stats["intensity_min"])
                    stats["intensity_max"] = mx if stats["intensity_max"] is None else max(mx, stats["intensity_max"])
            if i == 0:
                stride = max(1, len(xyz) // config["plot_sample_per_stream"])
                geometry_samples[stream] = xyz[::stride][:config["plot_sample_per_stream"]].astype(np.float64)
                figure_metadata[stream] = {"stamp_text": cloud.stamp_text, "pose_age_ms": age / 1e6 if age is not None else None, "transform": matrix.tolist() if matrix is not None else None}
                origins[stream] = matrix.tolist() if matrix is not None else None
            if i in (0, len(group)//2, len(group)-1):
                stride = max(1, len(xyz) // config["plot_sample_per_stream"])
                repeat_samples[(stream, i)] = xyz[::stride][:config["plot_sample_per_stream"]].astype(np.float64)
            if (i + 1) % 10 == 0:
                log.append(f"{stream}: processed {i+1}/{len(group)} clouds")
        stream_stats[stream] = stats
    # Diagnostic overlap only: no labels or hand alignment.
    overlap = []
    if "top" in geometry_samples and "dome" in geometry_samples:
        def voxels(points):
            return {tuple(x) for x in np.floor(points / 0.5).astype(np.int64)}
        for i in (0, 25, 49):
            a, b = voxels(repeat_samples[("top", i)]), voxels(repeat_samples[("dome", i)])
            overlap.append({"sample_index": i, "resolution_m": 0.5, "top_voxels": len(a), "dome_voxels": len(b), "intersection": len(a & b), "jaccard": len(a & b) / len(a | b) if a or b else None, "interpretation": "sampled occupancy overlap is viewpoint dependent; not a calibration fit"})
    schema = {"archive": config["archive"], "archive_bytes": archive.stat().st_size, "archive_sha256": config["archive_sha256"], "license": config["license"], "member_count": len(inventory), "logical_member_bytes": sum(r["bytes"] for r in inventory if r["kind"] == "file"), "label_filenames_only": labels, "streams": name_diagnostics, "headers_first_middle_last": headers, "odometry": odometry, "selected_stats": stream_stats, "selected_paths": selected_names, "selected_bytes": total}
    timing = {"window_start_ns": start, "window_end_ns_exclusive": start + 5_000_000_000, "selected_count": len(cloud_names), "stream_to_principal": STREAM_PRINCIPAL, "rows": timing_rows, "receipt_assumption": config["receipt_assumption"], "short_subsecond_semantics": "left-pad digits to 9 per pinned devkit"}
    all_finite = all(v["nonfinite_xyz"] == 0 for v in stream_stats.values())
    vehicle_poses = all(len(pose_rows.get(s, [])) > 0 for s in ("003", "004", "laser"))
    feasibility = [
        {"component": "density", "status": "feasible" if all_finite else "conditional", "basis": "observed ASCII XYZ and point counts; sensor-specific raw counts", "limits": "no reference fit or decision threshold in R01"},
        {"component": "temporal_geometry", "status": "conditional" if vehicle_poses else "blocked", "basis": "latest-past odometry and source stamps available" if vehicle_poses else "missing odometry", "limits": "scan timing, deskewing and clock-error bounds unverified; static consistency requires review"},
        {"component": "cross_agent_geometry", "status": "conditional" if len({STREAM_PRINCIPAL[s] for s,v in selected.items() if v}) >= 2 else "blocked", "basis": "four principals in selected interval; map/top transforms and raw RSU conventions", "limits": "geometric overlap is not visibility; physical vehicle extrinsics and calibration not independently verified"},
        {"component": "kinematics", "status": "conditional", "basis": "twist columns are present and variable in CSV", "limits": "measurement provenance and frame semantics not established; no cloud integrity inference"},
        {"component": "intensity", "status": "excluded", "basis": "raw intensity preserved", "limits": "cross-device radiometric comparability not established"},
    ]
    geometry = {"top_map_translation_m": [-41.551, -51.878, -1.077], "dome_map_translation_m": [-41.507, -51.864, -1.340], "dome_origin_in_top_m": (TOP_FROM_MAP - DOME_FROM_MAP).tolist(), "vehicle_paired_z_m": {"cloud": -3.25, "pose_right_composed": 3.25, "net_raw_to_map": 0}, "raw_rsu_map_coordinates": True, "first_clouds": figure_metadata, "static_overlap": overlap}
    write_json(output / "T_R01_schema.json", schema)
    write_json(output / "T_R01_timing.json", timing)
    write_json(output / "T_R01_component_feasibility.json", feasibility)
    write_json(output / "geometry_diagnostics.json", geometry)
    make_figure(output / "F_R01_geometry.png", geometry_samples, figure_metadata, origins)
    log.append(f"peak_ru_maxrss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}; units=macOS bytes")
    (output / "execution.log").write_text("\n".join(log) + "\n")
    source_audit = ROOT / "planning/audit/2026-10-08-source-verification.json"
    audited_sources = json.loads(source_audit.read_text())
    manifest = {"stage": "R01", "run_id": run_id, "created_utc": datetime.now(timezone.utc).isoformat(), "dataset": config["dataset"], "revision": config["revision"], "source_url": config["source_url"], "license": config["license"], "config": config, "input_sha256": {str(archive.relative_to(ROOT)): digest(archive), str(config_path.relative_to(ROOT)): digest(config_path), **{str((raw/n).relative_to(ROOT)): digest(raw/n) for n in selected_names}}, "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in (ROOT / "src/valid_point/io/mixed_signals.py", ROOT / "scripts/intake_segment.py", source_audit)}, "audited_pinned_source_text_sha256": {entry["file"]: entry["sha256"] for entry in audited_sources["files"]}, "output_sha256": {str(p.relative_to(output)): digest(p) for p in output.iterdir() if p.is_file()}}
    write_json(output / "manifest.json", manifest)
    return output


if __name__ == "__main__":
    print(run())
