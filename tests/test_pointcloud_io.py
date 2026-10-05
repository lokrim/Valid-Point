"""The canonical reader preserves fields, counts and coordinates."""

import json
from pathlib import Path

import pytest

from valid_point.io.pointcloud import PointCloud, read_pointcloud, write_pointcloud
from valid_point.synthetic import generate_scene, load_synthetic_config


CONFIG = load_synthetic_config(Path(__file__).resolve().parents[1] / "configs/synthetic.json")


def test_roundtrip_nonempty_and_empty(tmp_path):
    scene = generate_scene(CONFIG, 0)
    for cloud_id in (scene.observations[0].cloud_id, scene.observations[3].cloud_id):
        cloud = scene.cloud(cloud_id)
        path = tmp_path / f"{cloud_id}.json"
        write_pointcloud(path, cloud)
        got = read_pointcloud(path)
        assert got == cloud
        assert got.count == len(got.points)
        assert got.fields == ("x_m", "y_m", "z_m", "intensity")
        assert got.xyz().shape == (cloud.count, 3)


def test_reader_rejects_count_and_field_corruption(tmp_path):
    path = tmp_path / "bad.json"
    write_pointcloud(path, PointCloud("native", ((1.0, 2.0, 3.0, 0.5),)))
    original = json.loads(path.read_text())
    for changed in ({**original, "count": 0}, {**original, "fields": ["x", "y", "z", "intensity"]},
                    {**original, "points": [[float("nan"), 2, 3, 0.5]]}):
        path.write_text(json.dumps(changed))
        with pytest.raises(ValueError):
            read_pointcloud(path)
