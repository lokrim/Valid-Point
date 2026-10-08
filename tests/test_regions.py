import json
from pathlib import Path

import numpy as np
import pytest

from valid_point.regions import count_fixed_tiles, make_fixed_grid, receiver_context


ROOT = Path(__file__).resolve().parents[1]


def _config():
    return json.loads((ROOT / "configs/spatial_tracks.json").read_text())


def _grid():
    config = _config()["gt_free_grid"]
    return make_fixed_grid(
        x_limits_m=tuple(config["x_limits_m"]), y_limits_m=tuple(config["y_limits_m"]),
        z_limits_m=tuple(config["z_limits_m"]), tile_size_m=tuple(config["tile_size_m"]),
        frozen_ns=config["frozen_ns"], receiver_frame=config["receiver_frame"],
    )


def test_receiver_grid_is_complete_frozen_and_includes_empty_regions():
    grid = _grid()
    assert len(grid.tiles) == 400
    assert len({tile.region_id for tile in grid.tiles}) == 400
    counts, outside = count_fixed_tiles(np.array([[0.1, 0.1, 0.0]]), grid)
    assert sum(counts.values()) == 1 and outside == 0
    assert sum(value == 0 for value in counts.values()) == 399


def test_half_open_boundaries_and_outside_roi_are_explicit():
    grid = _grid()
    points = np.array([
        [-50.0, -50.0, -1.0], [0.0, 0.0, 0.0], [49.999, 49.999, .999],
        [50.0, 0.0, 0.0], [0.0, 50.0, 0.0], [0.0, 0.0, 1.0],
    ])
    counts, outside = count_fixed_tiles(points, grid)
    assert sum(counts.values()) == 3
    assert outside == 3


def test_sender_points_cannot_change_region_definition():
    grid = _grid()
    before = grid.digest
    count_fixed_tiles(np.empty((0, 3)), grid)
    count_fixed_tiles(np.array([[999.0, 999.0, 0.0], [0.1, 0.1, 0.0]]), grid)
    assert grid.digest == before
    assert all(tile.region_id.startswith("gt_free:tile:") for tile in grid.tiles)


def test_receiver_context_has_only_trusted_range_or_documented_broad_fallback():
    assert receiver_context(receiver_range_m=24.0, range_bins_m=(25.0, 50.0), allow_broad_context=True) == (
        "receiver_range:lt_25m", "receiver_owned_range"
    )
    assert receiver_context(receiver_range_m=None, range_bins_m=(25.0, 50.0), allow_broad_context=True) == (
        "receiver_range:all", "broad_receiver_context"
    )
    assert receiver_context(receiver_range_m=None, range_bins_m=(25.0, 50.0), allow_broad_context=False) == (
        None, "RANGE_UNKNOWN"
    )
    with pytest.raises(ValueError):
        receiver_context(receiver_range_m=-1, range_bins_m=(25.0,), allow_broad_context=True)
