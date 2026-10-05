"""Whole-scene determinism, geometry and split isolation."""

from dataclasses import fields
import json
from pathlib import Path

import numpy as np
import pytest

from valid_point.contracts import DecisionInput
from valid_point.synthetic import (availability_measurement, generate_scene,
                                   load_synthetic_config, seed_role)


CONFIG = load_synthetic_config(Path(__file__).resolve().parents[1] / "configs/synthetic.json")


def test_scene_order_independence_and_seed_role_disjointness():
    seeds = [0, 100, 200, 300]
    forward = {seed: generate_scene(CONFIG, seed) for seed in seeds}
    reverse = {seed: generate_scene(CONFIG, seed) for seed in reversed(seeds)}
    assert forward == reverse
    assert {seed_role(CONFIG, seed) for seed in seeds} == set(CONFIG["seed_families"])
    with pytest.raises(ValueError, match="outside"):
        seed_role(CONFIG, 99)
    path = Path(__file__).resolve().parents[1] / "configs/synthetic.json"
    assert path.exists()  # frozen config is source, not a generated run product
    assert len({s for values in CONFIG["seed_families"].values() for s in values}) == 60


def test_overlapping_seed_families_rejected_and_truth_not_in_decision_input(tmp_path):
    broken = {**CONFIG, "seed_families": {**CONFIG["seed_families"], "reference": [0, 100]}}
    path = tmp_path / "overlap.json"
    path.write_text(json.dumps(broken))
    with pytest.raises(ValueError, match="overlap"):
        load_synthetic_config(path)
    assert not any("truth" in item.name or "occluded" in item.name for item in fields(DecisionInput))


def test_inverse_transform_and_unique_view_geometry():
    scene = generate_scene(CONFIG, 0)
    assert scene.evaluator_truth.occluded_sensor_ids == ("west_low", "west_high")
    assert scene.evaluator_truth.uniquely_useful_sensor_id == "north"
    counts = {o.sensor_id: o.point_count for o in scene.observations[:3]}
    assert counts["north"] == counts["west_low"] + 8
    for obs, transform in zip(scene.observations[:3], scene.transforms):
        native = scene.cloud(obs.cloud_id).xyz()
        assert np.allclose(transform.apply(transform.apply(native), inverse=True), native, atol=1e-12)
        assert transform.source_frame == scene.cloud(obs.cloud_id).frame


def test_empty_absent_and_unavailable_kinematics():
    scene = generate_scene(CONFIG, 0)
    empty, absent, late, malformed, no_kin = scene.observations[3:]
    assert availability_measurement(empty).value == 0
    assert availability_measurement(absent).value is None
    assert availability_measurement(late).value is None
    assert availability_measurement(malformed).value is None
    assert no_kin.sensor_role == "vehicle" and no_kin.samples == ()
    assert all(o.visibility == "unknown" for o in scene.observations)
