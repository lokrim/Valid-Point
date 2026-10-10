"""R04 segment-level split and lineage guards; no cloud or label access."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


def canonical_hash(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True)
class Fold:
    id: str
    test: str
    calibration: str
    reference: tuple[str, ...]


def validate_roles(roles: dict) -> tuple[Fold, ...]:
    expected = {"D": "mini_7", "C0": "mini_10", "C1": "mini_11", "C2": "mini_12", "C3": "mini_13", "H": "mini_14"}
    entries = [roles["development"], *roles["comparison"], roles["final"]]
    if {x["id"]: x["segment"] for x in entries} != expected or len(entries) != len(expected):
        raise ValueError("frozen segment roles changed or duplicated")
    for entry in entries:
        if entry["bytes"] <= 0 or len(entry["published_lfs_sha256"]) != 64:
            raise ValueError("invalid public archive metadata")
    if roles.get("replacements"):
        for item in roles["replacements"]:
            if not all(item.get(k) for k in ("date", "original", "replacement", "metadata_reason")):
                raise ValueError("replacement needs dated metadata-only reason")
            if item["reason_class"] not in {"archive_access", "packaging", "agent_coverage", "timing", "calibration_feasibility"}:
                raise ValueError("outcome-driven replacement forbidden")
        raise ValueError("this R04 freeze has no replacement amendment")
    folds = tuple(Fold(x["id"], x["test"], x["calibration"], tuple(x["reference"])) for x in roles["folds"])
    expected_folds = (
        Fold("F0", "C0", "C1", ("C2", "C3")), Fold("F1", "C1", "C2", ("C3", "C0")),
        Fold("F2", "C2", "C3", ("C0", "C1")), Fold("F3", "C3", "C0", ("C1", "C2")),
        Fold("FH", "H", "C3", ("C0", "C1", "C2")),
    )
    if folds != expected_folds:
        raise ValueError("fold table differs from canonical segment protocol")
    for fold in folds:
        if len({fold.test, fold.calibration, *fold.reference}) != 2 + len(fold.reference):
            raise ValueError("reference/calibration/test overlap")
    return folds


def validate_membership(rows: list[dict], fold: Fold, *, segment_by_role: dict[str, str]) -> None:
    """Reject segment/variant leakage before a row is used in fit or evaluation."""
    allowed = {"reference": set(fold.reference), "calibration": {fold.calibration}, "test": {fold.test}}
    seen: dict[tuple[str, str, str], str] = {}
    for row in rows:
        role = row["split_role"]
        segment = row["segment"]
        group = row["segment_role"]
        if role not in allowed or group not in allowed[role] or segment_by_role.get(group) != segment:
            raise ValueError("row outside frozen segment role")
        if role in {"reference", "calibration"} and (row.get("variant") != "clean" or row.get("clean") is not True):
            raise ValueError("fit/calibration variant leakage")
        key = (segment, row["sensor"], row["cloud_id"])
        previous = seen.setdefault(key, role)
        if previous != role:
            raise ValueError("same base event crosses split roles")
    # A different variant of a segment still belongs to its one frozen role.


def validate_lineage(reference_rows: list[dict], calibration_rows: list[dict], test_rows: list[dict],
                     *, fold: Fold, sensor: str, arm: str, version: str) -> dict:
    """Check actual-path IDs and sensor-specific threshold ancestry."""
    if not reference_rows or not calibration_rows:
        raise ValueError("missing actual-path reference or calibration rows")
    for rows, expected_roles, required_clean in ((reference_rows, set(fold.reference), True),
                                                 (calibration_rows, {fold.calibration}, True),
                                                 (test_rows, {fold.test}, False)):
        for row in rows:
            if row["segment_role"] not in expected_roles or row["sensor"] != sensor:
                raise ValueError("sensor/segment lineage mismatch")
            if required_clean and (row.get("variant") != "clean" or not row.get("clean")):
                raise ValueError("nonclean fit/calibration lineage")
            if not row.get("cloud_sha256") or not row.get("cloud_id") or not row.get("raw_record_id"):
                raise ValueError("lineage lacks actual reader/raw record identity")
    if {r["segment_role"] for r in reference_rows} != set(fold.reference):
        raise ValueError("incomplete frozen reference segment set")
    ref_ids = {r["raw_record_id"] for r in reference_rows}
    cal_ids = {r["raw_record_id"] for r in calibration_rows}
    test_ids = {r["raw_record_id"] for r in test_rows}
    if ref_ids & cal_ids or ref_ids & test_ids or cal_ids & test_ids:
        raise ValueError("reference/calibration/test raw IDs overlap")
    threshold_id = canonical_hash({"fold": fold.id, "sensor": sensor, "arm": arm, "version": version,
                                   "reference_ids": sorted(ref_ids), "calibration_ids": sorted(cal_ids)})
    return {"fold": fold.id, "sensor": sensor, "arm": arm, "version": version,
            "reference_segments": list(fold.reference), "calibration_segment": fold.calibration,
            "test_segment": fold.test, "reference_rows": len(ref_ids), "calibration_rows": len(cal_ids),
            "test_rows": len(test_ids), "threshold_id": threshold_id}


def validate_threshold_use(threshold: dict, *, fold: Fold, sensor: str, arm: str, version: str) -> None:
    if any(threshold.get(k) != value for k, value in
           (("fold", fold.id), ("sensor", sensor), ("arm", arm), ("version", version),
            ("calibration_segment", fold.calibration), ("test_segment", fold.test))):
        raise ValueError("threshold lineage mismatch")
    if threshold.get("reference_segments") != list(fold.reference) or not threshold.get("threshold_id"):
        raise ValueError("reference lineage mismatch")
