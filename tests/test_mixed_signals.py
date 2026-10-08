from __future__ import annotations

import io
from pathlib import Path
import tarfile

import numpy as np
import pytest

from valid_point.io.mixed_signals import (
    extract_selected, id_coverage, latest_past, nearest_reference, optional_twist, parse_cloud_name,
    parse_stamp, pose_matrix, raw_to_top, read_pcd, read_pcd_header,
    safe_members, select_window, transform_xyz,
)


def test_short_subsecond_legacy_exact_ns():
    assert parse_stamp("1712121167", "80167605") == 1712121167080167605
    assert parse_stamp("1", "1") == 1_000_000_001
    assert parse_stamp("1", "000000001") == 1_000_000_001
    assert parse_cloud_name("PointClouds/mini_7/top_9_1.1.pcd").stamp_text == "1.1"
    with pytest.raises(ValueError):
        parse_stamp("1", "1234567890")


def test_explicit_ids_and_earliest_two_principal_window():
    names = [parse_cloud_name(f"{s}_{i}_{sec}.000000001.pcd") for s, i, sec in (
        ("top", 1, 1), ("dome", 1, 1), ("003", 0, 9), ("004", 3, 10),
    )]
    start, selected = select_window(names)
    assert start == 9_000_000_001
    assert selected["top"] == []
    assert [c.sync_id for c in selected["003"]] == [0]
    assert {c.principal for group in selected.values() for c in group} == {"003", "004"}


def test_duplicate_and_missing_ids():
    clouds = [parse_cloud_name(f"top_{i}_1.000000001.pcd") for i in (0, 2, 2, 4)]
    assert id_coverage(clouds) == ({2: 2}, [1, 3])


@pytest.mark.parametrize("line", [
    b"POINTS 3\nDATA ascii\n",  # missing vectors
    b"FIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH 2\nHEIGHT 1\nPOINTS 3\nDATA ascii\n",
    b"FIELDS x y z\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\nWIDTH 2\nHEIGHT 1\nPOINTS 2\nDATA ascii\n",
])
def test_malformed_headers_rejected(line):
    with pytest.raises(ValueError):
        read_pcd_header(io.BytesIO(line))


def test_pcd_count_and_finite_values():
    header = b"FIELDS x y z intensity\nSIZE 4 4 4 4\nTYPE F F F F\nCOUNT 1 1 1 1\nWIDTH 2\nHEIGHT 1\nPOINTS 2\nDATA ascii\n"
    parsed, values = read_pcd(io.BytesIO(header + b"1 2 3 7\n4 5 6 8\n"))
    assert parsed.points == 2 and parsed.fields == ("x", "y", "z", "intensity")
    assert np.isfinite(values).all()
    with pytest.raises(ValueError, match="body count"):
        read_pcd(io.BytesIO(header + b"1 2 3 7\n"))


def make_tar(path: Path, members: list[tuple[str, bytes, bytes | None]]):
    with tarfile.open(path, "w") as tar:
        for name, data, kind in members:
            info = tarfile.TarInfo(name)
            info.type = kind or tarfile.REGTYPE
            info.size = len(data) if info.type == tarfile.REGTYPE else 0
            tar.addfile(info, io.BytesIO(data) if info.type == tarfile.REGTYPE else None)


@pytest.mark.parametrize("members", [
    [("../outside", b"x", None)],
    [("a", b"x", None), ("a", b"y", None)],
    [("link", b"", tarfile.SYMTYPE)],
    [("special", b"", tarfile.CHRTYPE)],
    [("parent", b"x", None), ("parent/child", b"y", None)],
])
def test_unsafe_tar_rejected(tmp_path, members):
    path = tmp_path / "bad.tar"
    make_tar(path, members)
    with pytest.raises(ValueError):
        safe_members(path)


def test_safe_bounded_extraction(tmp_path):
    path = tmp_path / "ok.tar"
    make_tar(path, [("dir/cloud.pcd", b"12345", None)])
    inventory = safe_members(path)
    with pytest.raises(ValueError):
        extract_selected(path, tmp_path / "raw", ["dir/cloud.pcd"], inventory, cap=4)
    assert extract_selected(path, tmp_path / "raw", ["dir/cloud.pcd"], inventory, cap=5) == 5
    assert (tmp_path / "raw/dir/cloud.pcd").read_bytes() == b"12345"


def test_quaternion_frame_composition_and_inverse():
    pose = pose_matrix((1, 2, 3), (np.sqrt(0.5), 0, 0, np.sqrt(0.5)))
    top = raw_to_top("003", pose)
    point = np.array([[3.0, 4.0, 5.0]])
    mapped = transform_xyz(point, top)
    recovered = transform_xyz(mapped, np.linalg.inv(top))
    np.testing.assert_allclose(recovered, point, atol=1e-12)
    np.testing.assert_allclose(top[:3, 3], [42.551, 53.878, 4.077], atol=1e-12)
    shift_up = np.eye(4)
    shift_up[2, 3] = 3.25
    shift_down = np.eye(4)
    shift_down[2, 3] = -3.25
    np.testing.assert_allclose(pose @ shift_up @ shift_down, pose)
    with pytest.raises(ValueError):
        pose_matrix((0, 0, 0), (2, 0, 0, 0))


def test_causal_past_rejects_future_nearest():
    stamps = [100, 200, 300]
    assert latest_past(stamps, 90) is None
    assert latest_past(stamps, 149) == 0
    assert latest_past(stamps, 200) == 1
    assert nearest_reference(stamps, 190) == 1
    assert latest_past(stamps, 190) == 0


def test_missing_or_invalid_velocity_stays_unavailable():
    assert optional_twist({}) is None
    assert optional_twist({"field.twist.twist.linear.x": "1"}) is None
    row = {f"field.twist.twist.linear.{axis}": value for axis, value in zip("xyz", ("1", "2", "3"))}
    assert optional_twist(row) == (1.0, 2.0, 3.0)
    row["field.twist.twist.linear.z"] = "nan"
    assert optional_twist(row) is None


def test_observed_local_header_if_intake_data_available():
    root = Path(__file__).resolve().parents[1]
    path = root / "data/mixed_signals/1a61aea747aa6bc45da2c2f085a1f1d3abc41f91/raw/PointClouds/mini_7/003_0_1712121167.80167605.pcd"
    if not path.exists():
        pytest.skip("selected R01 extraction has not run")
    with path.open("rb") as handle:
        header, values = read_pcd(handle)
    assert header.width == 2048 and header.height == 128 and header.points == 262144
    assert header.encoding == "ascii" and header.fields == ("x", "y", "z", "intensity")
    assert len(values) == 262144
    assert np.isfinite(values[:, :3]).all()
