"""Causal boundaries and distinct unknown values."""

from dataclasses import replace

import pytest

from valid_point.contracts import (CausalSample, DecisionKey, EvidenceStatus,
                                   RawMeasurement, assert_unique_keys)
from valid_point.synthetic import generate_scene, load_synthetic_config
from pathlib import Path


CONFIG = load_synthetic_config(Path(__file__).resolve().parents[1] / "configs/synthetic.json")


def test_exact_deadline_inclusive_and_one_nanosecond_late():
    scene = generate_scene(CONFIG, 0)
    empty = scene.observations[3]
    assert empty.arrival_ns == empty.key.deadline_ns
    assert empty.point_count == 0
    with pytest.raises(ValueError, match="deadline"):
        replace(empty, arrival_ns=empty.key.deadline_ns + 1)
    with pytest.raises(ValueError, match="unavailable sample"):
        replace(empty, samples=(CausalSample("future", empty.source_ns,
                                             empty.key.deadline_ns + 1, None, None),))


def test_duplicate_decision_keys_rejected():
    scene = generate_scene(CONFIG, 0)
    with pytest.raises(ValueError, match="duplicate decision"):
        assert_unique_keys([scene.observations[0], scene.observations[0]])


def test_unknown_is_never_numeric_zero_and_static_is_not_applicable():
    key = DecisionKey("episode", "sender", 1, 10)
    with pytest.raises(ValueError, match="unknown"):
        RawMeasurement(key, "count", 0.0, "points", EvidenceStatus.UNKNOWN, "absent", None, ())
    with pytest.raises(ValueError, match="finite"):
        RawMeasurement(key, "count", None, "points", EvidenceStatus.KNOWN, "", 10, ())
