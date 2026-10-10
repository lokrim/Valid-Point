"""R04 arithmetic/identity fixtures only; no empirical calibration."""
import json
from pathlib import Path
import pytest

from valid_point.evaluation.splits import (validate_roles, validate_membership,
                                           validate_lineage, validate_threshold_use)

ROOT = Path(__file__).resolve().parents[1]


def roles():
    return json.loads((ROOT / "configs/segment_roles.json").read_text())


def test_exact_folds_and_disjointness():
    folds = validate_roles(roles())
    assert len(folds) == 5
    assert folds[-1].reference == ("C0", "C1", "C2")
    assert folds[-1].calibration == "C3" and folds[-1].test == "H"
    bad = roles(); bad["folds"][0]["reference"][0] = "C0"
    with pytest.raises(ValueError): validate_roles(bad)


def test_segment_variant_leakage_rejected():
    fold = validate_roles(roles())[0]
    mapping = {x["id"]: x["segment"] for x in [roles()["development"], *roles()["comparison"], roles()["final"]]}
    row = {"split_role": "reference", "segment_role": "C2", "segment": "mini_12",
           "variant": "clean", "clean": True, "sensor": "003", "cloud_id": "a"}
    validate_membership([row], fold, segment_by_role=mapping)
    with pytest.raises(ValueError): validate_membership([dict(row, variant="attacked")], fold, segment_by_role=mapping)
    with pytest.raises(ValueError): validate_membership([dict(row, segment="mini_10")], fold, segment_by_role=mapping)
    with pytest.raises(ValueError): validate_membership([row, dict(row, split_role="test")], fold, segment_by_role=mapping)


def test_actual_path_sensor_threshold_lineage():
    fold = validate_roles(roles())[0]
    def row(group, stem):
        return {"segment_role": group, "sensor": "003", "variant": "clean", "clean": True,
                "cloud_id": stem, "raw_record_id": stem, "cloud_sha256": "a"*64}
    ref = [row("C2", "r2"), row("C3", "r3")]
    cal = [row("C1", "c1")]
    test = [dict(row("C0", "t0"), variant="attacked", clean=False)]
    lineage = validate_lineage(ref, cal, test, fold=fold, sensor="003", arm="D-only", version="memoryless")
    validate_threshold_use(lineage, fold=fold, sensor="003", arm="D-only", version="memoryless")
    with pytest.raises(ValueError): validate_threshold_use(lineage, fold=fold, sensor="004", arm="D-only", version="memoryless")
    with pytest.raises(ValueError): validate_lineage(ref, [dict(cal[0], raw_record_id="r2")], test,
                                                    fold=fold, sensor="003", arm="D-only", version="memoryless")
    with pytest.raises(ValueError): validate_lineage(ref[:1], cal, test, fold=fold, sensor="003", arm="D-only", version="memoryless")


def test_temporal_warmup_and_sensor_calibration_power():
    from valid_point.temporal import TemporalEWMA
    from valid_point.calibration import calibrate
    from valid_point.evaluation.metrics import threshold_power
    state = TemporalEWMA(tau_s=1, g_reset_s=.5, min_updates=10)
    records = [state.update(episode="e", principal="003", sensor="003", method_arm="D-only",
                            reference_version="r", source_ns=i*100_000_000, A=.4) for i in range(32)]
    assert records[9].ready is False and records[9].reason == "WARM_UP"
    assert records[30].ready is True
    rows = [{"split_role": "calibration", "clean": True, "seed": 0, "segment": "mini_11",
             "status": "known", "A": .4} for _ in range(199)]
    assert calibrate(rows).status == "unavailable"
    assert threshold_power([.4]*199, None) == "INSUFFICIENT_KNOWN"
    assert calibrate(rows + [dict(rows[0])]).threshold == .4
    assert threshold_power([.4]*200, .4) == "NO_POWER"
    assert threshold_power([.4]*200, 1.) == "NO_POWER"
