"""Tiny deterministic S01 scenes. Evaluator truth is separate from causal inputs."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np

from .contracts import (DecisionInput, DecisionKey, EvidenceStatus,
                        MessageState, RawMeasurement, RigidTransform, assert_unique_keys)
from .io.pointcloud import PointCloud


@dataclass(frozen=True)
class EvaluatorTruth:
    """Offline geometry/visibility labels. Never pass to GT-free score or policy."""

    object_centers_m: tuple[tuple[float, float, float], ...]
    occluded_sensor_ids: tuple[str, ...]
    uniquely_useful_sensor_id: str
    wall_x_m: float
    wall_y_interval_m: tuple[float, float]


@dataclass(frozen=True)
class SyntheticScene:
    seed: int
    split_role: str
    observations: tuple[DecisionInput, ...]
    transforms: tuple[RigidTransform, ...]
    clouds: tuple[tuple[str, PointCloud], ...]
    evaluator_truth: EvaluatorTruth

    def cloud(self, cloud_id: str) -> PointCloud:
        return dict(self.clouds)[cloud_id]


def load_synthetic_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    expected = {"schema_version", "stage", "track", "episode", "anchor_ns", "deadline_delta_ns",
                "latency_ns", "seed_families", "rng_scheme", "units", "time_mapping",
                "reference_lineage", "calibration_lineage", "security_groups"}
    if set(config) != expected or config["stage"] != "S01" or config["track"] != "gt_free_contract_only":
        raise ValueError("invalid S01 configuration")
    families = {name: set(values) for name, values in config["seed_families"].items()}
    if set(families) != {"development", "reference", "calibration", "test"}:
        raise ValueError("missing seed role")
    if any(len(values) != len(families[name]) or any(type(v) is not int or v < 0 for v in values)
           for name, values in config["seed_families"].items()):
        raise ValueError("invalid or duplicate seeds")
    if sum(map(len, families.values())) != len(set().union(*families.values())):
        raise ValueError("seed roles overlap")
    if config["deadline_delta_ns"] < 0 or config["latency_ns"] < 0:
        raise ValueError("negative timing")
    if len(set(config["security_groups"].values())) != len(config["security_groups"]):
        raise ValueError("security groups must be independent")
    return config


def seed_role(config: dict, seed: int) -> str:
    matches = [role for role, values in config["seed_families"].items() if seed in values]
    if len(matches) != 1:
        raise ValueError("seed outside frozen families")
    return matches[0]


def _transform(sensor_id: str, x: float, y: float, yaw_deg: float, anchor_ns: int) -> RigidTransform:
    yaw = np.deg2rad(yaw_deg)
    c, s = float(np.cos(yaw)), float(np.sin(yaw))
    return RigidTransform(
        transform_id=f"receiver_from_{sensor_id}", source_frame=f"{sensor_id}_native",
        target_frame="receiver", matrix=((c, -s, 0.0, x), (s, c, 0.0, y),
                                         (0.0, 0.0, 1.0, 1.5), (0.0, 0.0, 0.0, 1.0)),
        valid_from_ns=anchor_ns - 1_000_000_000, valid_until_ns=anchor_ns + 1_000_000_000,
        provenance="synthetic fixed extrinsic; yaw about +z; native right-handed x forward/y left/z up")


def _wall_blocks(sensor_xy: tuple[float, float], target_xy: tuple[float, float]) -> bool:
    x0, y0 = sensor_xy
    x1, y1 = target_xy
    if (x0 - 0.0) * (x1 - 0.0) >= 0 or x1 == x0:
        return False
    fraction = -x0 / (x1 - x0)
    y_cross = y0 + fraction * (y1 - y0)
    return -2.0 <= y_cross <= 2.0


def generate_scene(config: dict, seed: int) -> SyntheticScene:
    """One complete scene uses one seed; no global RNG or traversal state."""
    role = seed_role(config, seed)
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    anchor = int(config["anchor_ns"])
    deadline = anchor + int(config["deadline_delta_ns"])
    object_x = 2.0 + float(rng.uniform(-0.12, 0.12))
    target = (object_x, 0.0, 0.75)
    sensors = (("west_low", -5.0, -1.0, 0.0), ("west_high", -5.0, 1.0, 25.0),
               ("north", 2.0, 5.0, -90.0))
    transforms = tuple(_transform(sid, x, y, yaw, anchor) for sid, x, y, yaw in sensors)
    observations = []
    clouds = []
    occluded = []
    for (sid, x, y, _), transform in zip(sensors, transforms):
        blocked = _wall_blocks((x, y), target[:2])
        if blocked:
            occluded.append(sid)
        # Static wall returns and road-plane returns; target returns only with line of sight.
        wall = np.asarray([(0.0, wy, z) for wy in (-2.0, -1.0, 0.0, 1.0, 2.0)
                           for z in (0.3, 1.2)], dtype=float)
        road = np.asarray([(-2.0, -3.0, 0.0), (1.0, 3.0, 0.0)], dtype=float)
        target_points = np.asarray([(object_x + dx, dy, z) for dx in (-0.4, 0.4)
                                    for dy in (-0.3, 0.3) for z in (0.3, 1.2)], dtype=float)
        receiver_xyz = np.concatenate((wall, road, target_points if not blocked else np.empty((0, 3))))
        native_xyz = transform.apply(receiver_xyz, inverse=True)
        cloud_id = f"scene_{seed}_{sid}"
        cloud = PointCloud(frame=transform.source_frame,
                           points=tuple(tuple(float(v) for v in (*point, 1.0)) for point in native_xyz))
        clouds.append((cloud_id, cloud))
        observations.append(DecisionInput(
            key=DecisionKey(config["episode"] + f"_{seed}", sid, 0, deadline),
            sensor_id=sid, security_group=config["security_groups"][sid], sensor_role="static_rsu",
            anchor_ns=anchor, source_ns=anchor, arrival_ns=anchor + int(config["latency_ns"]),
            message_state=MessageState.PRESENT_NONEMPTY, cloud_id=cloud_id,
            point_count=cloud.count, transform_id=transform.transform_id))
    # Independent counterexamples share the same source time but distinct decision frames.
    for frame_id, state, arrival, count, cloud_id in (
        (1, MessageState.PRESENT_EMPTY, deadline, 0, f"scene_{seed}_empty"),
        (2, MessageState.ABSENT, None, None, None),
        (3, MessageState.LATE, deadline + 1, None, f"scene_{seed}_late"),
        (4, MessageState.MALFORMED, deadline, None, f"scene_{seed}_malformed"),
        (5, MessageState.PRESENT_NONEMPTY, deadline, 1, f"scene_{seed}_no_kinematics")):
        if state is MessageState.PRESENT_EMPTY:
            clouds.append((cloud_id, PointCloud(frame="north_native", points=())))
        if frame_id == 5:
            clouds.append((cloud_id, PointCloud(frame="vehicle_native", points=((1.0, 0.0, 0.0, 1.0),))))
        observations.append(DecisionInput(
            key=DecisionKey(config["episode"] + f"_{seed}", "fixture_sender", frame_id, deadline),
            sensor_id="vehicle" if frame_id == 5 else "north",
            security_group=config["security_groups"]["vehicle" if frame_id == 5 else "north"],
            sensor_role="vehicle" if frame_id == 5 else "static_rsu", anchor_ns=anchor,
            source_ns=anchor if state is not MessageState.ABSENT else None,
            arrival_ns=arrival, message_state=state, cloud_id=cloud_id, point_count=count,
            transform_id=None if frame_id == 5 else transforms[2].transform_id,
            samples=() if frame_id == 5 else ()))
    assert_unique_keys(observations)
    truth = EvaluatorTruth(object_centers_m=(target, (object_x + 0.4, 0.0, 0.75)),
                           occluded_sensor_ids=tuple(occluded), uniquely_useful_sensor_id="north",
                           wall_x_m=0.0, wall_y_interval_m=(-2.0, 2.0))
    return SyntheticScene(seed, role, tuple(observations), transforms, tuple(clouds), truth)


def availability_measurement(row: DecisionInput) -> RawMeasurement:
    """A count is raw data only; zero never becomes a removal accusation."""
    if row.message_state in (MessageState.PRESENT_NONEMPTY, MessageState.PRESENT_EMPTY):
        return RawMeasurement(row.key, "point_count", float(row.point_count), "points",
                              EvidenceStatus.KNOWN, "parsed by deadline; visibility unknown",
                              row.arrival_ns, (row.cloud_id,))
    reason = {MessageState.ABSENT: "no message by deadline",
              MessageState.LATE: "arrival after deadline",
              MessageState.MALFORMED: "parser rejected payload"}[row.message_state]
    return RawMeasurement(row.key, "point_count", None, "points", EvidenceStatus.UNKNOWN,
                          reason, None, ())


def kinematics_availability(row: DecisionInput) -> RawMeasurement:
    if row.sensor_role == "static_rsu":
        return RawMeasurement(row.key, "kinematics", None, "m", EvidenceStatus.NOT_APPLICABLE,
                              "predeclared static sensor role", None, ())
    return RawMeasurement(row.key, "kinematics", None, "m", EvidenceStatus.UNKNOWN,
                          "no causal pose/velocity samples", None, ())


def scene_contract_rows(scene: SyntheticScene) -> list[dict[str, str]]:
    transform_by_id = {t.transform_id: t for t in scene.transforms}
    rows = []
    for obs in scene.observations:
        t = transform_by_id.get(obs.transform_id)
        rows.append({"episode": obs.key.episode, "sender": obs.key.sender,
                     "security_group": obs.security_group, "sensor_role": obs.sensor_role,
                     "frame_id": str(obs.key.frame_id), "native_frame": t.source_frame if t else "unavailable",
                     "receiver_frame": t.target_frame if t else "unavailable",
                     "transform_id": obs.transform_id or "unknown",
                     "source_ns": str(obs.source_ns) if obs.source_ns is not None else "null",
                     "arrival_ns": str(obs.arrival_ns) if obs.arrival_ns is not None else "null",
                     "anchor_ns": str(obs.anchor_ns), "deadline_ns": str(obs.key.deadline_ns),
                     "message_state": obs.message_state.value, "point_count": str(obs.point_count) if obs.point_count is not None else "null",
                     "visibility": obs.visibility})
    return rows


def unknown_state_rows(scene: SyntheticScene) -> list[dict[str, str]]:
    rows = []
    for obs in scene.observations:
        point = availability_measurement(obs)
        motion = kinematics_availability(obs)
        rows.append({"sender": obs.key.sender, "frame_id": str(obs.key.frame_id),
                     "message_state": obs.message_state.value, "raw_count": str(point.value) if point.value is not None else "null",
                     "count_status": point.status.value, "count_reason": point.reason,
                     "kinematics_status": motion.status.value, "kinematics_reason": motion.reason,
                     "visibility": obs.visibility, "removal_inference": "unknown"})
    return rows


def point_rows(scene: SyntheticScene) -> list[dict[str, str]]:
    """Complete small native/receiver point table for the uniquely useful view."""
    obs = next(o for o in scene.observations if o.sensor_id == "north" and o.key.frame_id == 0)
    transform = next(t for t in scene.transforms if t.transform_id == obs.transform_id)
    cloud = scene.cloud(obs.cloud_id)
    receiver = transform.apply(cloud.xyz())
    rows = []
    for index, (native, mapped) in enumerate(zip(cloud.points, receiver)):
        rows.append({"point_id": str(index), "sensor": "north", "native_frame": cloud.frame,
                     "native_x_m": f"{native[0]:.6f}", "native_y_m": f"{native[1]:.6f}",
                     "native_z_m": f"{native[2]:.6f}", "receiver_x_m": f"{mapped[0]:.6f}",
                     "receiver_y_m": f"{mapped[1]:.6f}", "receiver_z_m": f"{mapped[2]:.6f}",
                     "intensity": f"{native[3]:.1f}"})
    return rows


def scene_figure(scene: SyntheticScene, report_dir: Path, provenance: dict[str, str]) -> list[Path]:
    """Plan and elevation of input geometry; truth annotations are visibly evaluator only."""
    from .provenance import output_stem, sha256_file, write_json_new
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle

    stem = output_stem("F01_scene_views", provenance)
    paths = [report_dir / f"{stem}.{ext}" for ext in ("pdf", "svg", "png", "provenance.json")]
    if any(path.exists() for path in paths):
        raise FileExistsError(stem)
    report_dir.mkdir(parents=True, exist_ok=True)
    fig = Figure(figsize=(11, 5), dpi=170)
    top, elevation = fig.subplots(1, 2)
    top.set_facecolor("#f1f1ed")
    top.add_patch(Rectangle(
        (-10, -6), 20, 12, facecolor="#e3e5e7", edgecolor="#89939a", alpha=.75,
        label="road plane z=0 m"))
    top.plot([0, 0], [-2, 2], color="#3d4246", linewidth=8, label="static wall")
    centers = scene.evaluator_truth.object_centers_m
    top.plot([c[0] for c in centers], [c[1] for c in centers], "o--", color="#bd4b1d",
             label="moving object centers (evaluator truth)")
    for obs, transform in zip(scene.observations[:3], scene.transforms):
        m = np.asarray(transform.matrix)
        x, y = m[0, 3], m[1, 3]
        blocked = obs.sensor_id in scene.evaluator_truth.occluded_sensor_ids
        color = "#9b4444" if blocked else "#147b55"
        top.plot([x, centers[0][0]], [y, centers[0][1]], linestyle=":" if blocked else "-",
                 color=color, linewidth=1.7)
        top.scatter([x], [y], color=color, s=65)
        top.text(x + .1, y + .15, obs.sensor_id, fontsize=8)
        top.arrow(x, y, m[0, 0] * .65, m[1, 0] * .65, color="#23395d",
                  head_width=.13, length_includes_head=True)
        top.arrow(x, y, m[0, 1] * .65, m[1, 1] * .65, color="#7851a9",
                  head_width=.13, length_includes_head=True)
    north = scene.observations[2]
    receiver_points = scene.transforms[2].apply(scene.cloud(north.cloud_id).xyz())
    top.scatter(receiver_points[:, 0], receiver_points[:, 1], s=8, color="#1776b5",
                label=f"north returns n={len(receiver_points)}")
    top.annotate("receiver +x", xy=(6, -5), xytext=(2, -5), arrowprops={"arrowstyle": "->"})
    top.annotate("receiver +y", xy=(8, -2), xytext=(8, -5), arrowprops={"arrowstyle": "->"})
    top.set(xlim=(-7, 10), ylim=(-6, 6), xlabel="receiver x (m)", ylabel="receiver y (m)",
            title="Top view: dashed sight lines are wall-occluded")
    top.set_aspect("equal")
    top.legend(loc="lower left", fontsize=7)
    elevation.plot([-10, 10], [0, 0], color="#777", linewidth=3, label="road plane")
    elevation.fill_between([-.12, .12], [0, 0], [1.5, 1.5], color="#3d4246", label="wall")
    for center in centers:
        elevation.add_patch(Rectangle(
            (center[0] - .4, .3), .8, .9, facecolor="#bd4b1d", alpha=.35))
    elevation.scatter(receiver_points[:, 0], receiver_points[:, 2], s=10, color="#1776b5",
                      label="north returns")
    elevation.set(xlim=(-6, 6), ylim=(-.2, 2.2), xlabel="receiver x (m)", ylabel="receiver z (m)",
                  title="Elevation: wall, road, target returns")
    elevation.legend(fontsize=8)
    fig.suptitle(f"F01_scene_views · seed {scene.seed} · {scene.split_role} · {provenance['run_id']}\n"
                 "Blue/purple arrows: native +x/+y; green: unique honest view; visibility labels evaluator only",
                 fontsize=10)
    fig.tight_layout()
    for path in paths[:3]:
        fig.savefig(path, bbox_inches="tight")
    write_json_new(paths[3], {**provenance, "name": "F01_scene_views",
                              "outputs": {path.name: sha256_file(path) for path in paths[:3]}})
    return paths
