#!/usr/bin/env python3
"""R04 metadata-only protocol freeze. Does not open C/H archives or labels."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from valid_point.evaluation.splits import canonical_hash, validate_roles  # noqa: E402


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def table(run: Path, name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("empty frozen table")
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with (run / (name + ".csv")).open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows({k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in rows)
    def escape(v):
        return str(v).replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(keys) + " |", "| " + " | ".join("---" for _ in keys) + " |"]
    lines += ["| " + " | ".join(escape(json.dumps(row.get(k), sort_keys=True) if isinstance(row.get(k), (dict, list)) else row.get(k, "")) for k in keys) + " |" for row in rows]
    (run / (name + ".md")).write_text(f"# {name}\n\nR04 frozen protocol table; public metadata and declared rules, not outcomes.\n\n" + "\n".join(lines) + "\n")


def main() -> None:
    started = time.monotonic()
    roles_path = ROOT / "configs/segment_roles.json"
    method_path = ROOT / "configs/replay_evaluation.json"
    roles = json.loads(roles_path.read_text())
    method = json.loads(method_path.read_text())
    folds = validate_roles(roles)
    if method["resource_plan"]["comparison_final_download_authorized"] or method["resource_plan"]["retention_budget_bytes_authorized"] is not None:
        raise ValueError("resource authorization must cite actual evidence before being recorded as granted")
    if method["selected_arms"] != ["D-only", "G-only", "max(D,G)"]:
        raise ValueError("arm change needs a documented pre-exposure amendment")
    if method["replay"]["families"] != {"random_removal": [.1, .3, .6], "localized_removal": [.25, .5, 1.],
                                         "displacement_m": [.2, 1., 3.], "rearrangement_m": [.2, 1., 3.],
                                         "addition_fraction": [.01, .05, .2]}:
        raise ValueError("attack grid differs from canonical method")
    source_paths = sorted([*ROOT.glob("src/valid_point/**/*.py"), *ROOT.glob("configs/*.json"),
                           ROOT / "scripts/freeze_protocol.py", ROOT / "notebooks/R04_protocol_freeze.ipynb",
                           ROOT / "tests/test_splits.py", ROOT / "tests/test_metrics.py",
                           *(ROOT / "planning" / p for p in ("README.md", "01_research_contract.md", "02_data_protocol.md",
                               "03_phase1_evidence.md", "06_attack_simulation.md", "07_validation.md", "08_notebooks.md",
                               "09_decisions_and_gates.md", "temporal_spec.md", "sources.md"))])
    source_hashes = {str(p.relative_to(ROOT)): digest(p) for p in source_paths}
    seed = method["replay"]["seed"]
    freeze_payload = {"schema": "R04.freeze.v1", "roles": roles, "method": method,
                      "source_sha256": source_hashes, "seed": seed,
                      "prior_GR3_manifest_sha256": digest(ROOT / "artifacts/20261010T155346Z-R03/manifest.json")}
    freeze_hash = canonical_hash(freeze_payload)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-R04-" + freeze_hash[:12]
    run = ROOT / "artifacts" / run_id
    run.mkdir(exist_ok=False)
    log = [f"UTC start {datetime.now(timezone.utc).isoformat()}", "R04 metadata-only; no C/H archive or label bodies opened"]
    try:
        write_json(run / "freeze_payload.json", freeze_payload)
        (run / "freeze.sha256").write_text(freeze_hash + "  freeze_payload.json (canonical JSON content)\n")
        split_rows = [{"fold": f.id, "reference_roles": list(f.reference),
                       "reference_segments": [next(x["segment"] for x in roles["comparison"] if x["id"] == c) for c in f.reference],
                       "calibration_role": f.calibration, "test_role": f.test,
                       "calibration_segment": next(x["segment"] for x in [*roles["comparison"], roles["final"]] if x["id"] == f.calibration),
                       "test_segment": next(x["segment"] for x in [*roles["comparison"], roles["final"]] if x["id"] == f.test),
                       "fit_rule": "actual clean reader/raw rows, >=200 distinct clouds/context across >=2 reference segments",
                       "calibration_rule": "separate actual clean reader/score/state rows, >=200 known per sensor/arm/version",
                       "prediction_barrier": "all folds and ablations sealed before outcomes"} for f in folds]
        table(run, "T_R04_splits", split_rows)
        parameter_rows = [{"section": key, "frozen_value": value, "source_config": str(method_path.relative_to(ROOT)),
                           "config_sha256": digest(method_path)} for key, value in method.items() if key != "resource_plan"]
        parameter_rows.append({"section": "resource_plan", "frozen_value": method["resource_plan"],
                               "source_config": str(method_path.relative_to(ROOT)), "config_sha256": digest(method_path)})
        table(run, "T_R04_parameters", parameter_rows)
        lineage_rows = [{"fold": f.id, "sensor": s, "arm": arm, "version": version,
                         "reference_roles": list(f.reference), "calibration_role": f.calibration, "test_role": f.test,
                         "threshold_key": canonical_hash([freeze_hash, f.id, s, arm, version]),
                         "actual_row_ids": "pending R05/R06; must hash reader cloud, causal raw row, pose/history and separate calibration score/state",
                         "status": "DECLARED_UNEXPOSED"} for f in folds for s in method["sensors"]
                        for arm in method["selected_arms"] for version in method["temporal_versions"]]
        table(run, "T_R04_lineage", lineage_rows)
        attack_rows = [{"family": family, "severity": severity, "schedule": schedule,
                        "per_comparison_segment": True, "target_principal": method["replay"]["principal"],
                        "seed": seed} for family, severities in method["replay"]["families"].items()
                       for severity in severities for schedule in method["replay"]["schedules_s"]]
        table(run, "T_R04_attack_grid", attack_rows)
        exposure = {"as_of_utc": datetime.now(timezone.utc).isoformat(), "development_archive": "mini_7 locally verified in GR1/R03",
                    "comparison_roles": [x["id"] for x in roles["comparison"]], "final_role": "H",
                    "comparison_final_cloud_bodies_loaded_by_R04": False, "comparison_final_label_bodies_loaded_by_R04": False,
                    "comparison_final_outcomes_computed": False, "public_archive_metadata_only": True,
                    "download_authorization": "ABSENT_IN_PROJECT_RECORD", "authorized_retention_budget_bytes": None,
                    "provisional_plan_bytes": method["resource_plan"]["provisional_full_study_reservation_bytes"],
                    "free_disk_bytes_at_freeze": shutil.disk_usage(ROOT).free,
                    "R05_R06_resource_disposition": "BLOCKED_UNTIL_EXPLICIT_AUTHORIZATION_AND_ACTUAL_BUDGET",
                    "freeze_sha256": freeze_hash}
        write_json(run / "exposure_ledger.json", exposure)
        test = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests",
                               "--junitxml=" + str(run / "test_results.xml")], cwd=ROOT,
                              env={**os.environ, "PYTHONPATH": str(ROOT / "src")}, capture_output=True, text=True)
        (run / "test.log").write_text(test.stdout + test.stderr)
        log.append(f"R04 focused tests exit={test.returncode}: {test.stdout.strip()}")
        import nbformat
        from nbclient import NotebookClient
        notebook = nbformat.read(ROOT / "notebooks/R04_protocol_freeze.ipynb", as_version=4)
        notebook_error = None
        try:
            os.environ["VP_RUN_DIR"] = str(run)
            notebook = NotebookClient(notebook, timeout=300, kernel_name="python3",
                                      resources={"metadata": {"path": str(ROOT)}}).execute()
        except Exception as exc:
            notebook_error = repr(exc)
            (run / "notebook_error.txt").write_text(notebook_error + "\n")
        nbformat.write(notebook, run / "R04_protocol_freeze.executed.ipynb")
        log.append(f"fresh notebook {'PASS' if notebook_error is None else notebook_error}")
        status = "PASS" if test.returncode == 0 and notebook_error is None else "BLOCKED"
        environment = {"python": sys.version, "platform": platform.platform(), "wall_s": time.monotonic()-started,
                       "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       "free_disk_bytes_end": shutil.disk_usage(ROOT).free}
        write_json(run / "environment.json", environment)
        (run / "execution.log").write_text("\n".join(log) + "\n")
        gate = (f"# GR4 — sealed comparison protocol\n\nTechnical status: **{status}**. Scientific outcomes: **unexposed**.\n\n"
                f"Frozen content SHA-256: `{freeze_hash}`. Segment roles, all five fold lineages, 30 nonzero episodes per comparison segment, "
                "all named arms and benign controls, scorer/evaluator separation, attempted denominators, no-power/undefined handling and all-fold prediction sealing are fixed. "
                "T_R04_splits, T_R04_parameters and T_R04_lineage are reviewable CSV/Markdown. The lineage table declares keys; "
                "actual row/cloud IDs cannot exist before R05/R06 and are mandatory then. Arithmetic test fixtures are not empirical calibration.\n\n"
                "Resource disposition: **R05/R06 acquisition blocked**. No comparison/final download authorization or actual retention budget is recorded; "
                f"free disk at freeze was {exposure['free_disk_bytes_at_freeze']} bytes versus the provisional 80,000,000,000-byte reservation. "
                "No comparison/final archive or label body was opened, no outcomes computed, and no acquisition or evaluation was launched.\n")
        (run / "gate.md").write_text(gate)
        git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        git_dirty = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True).stdout
        manifest = {"stage": "R04", "run_id": run_id, "technical_status": status, "freeze_sha256": freeze_hash,
                    "freeze_payload_sha256": digest(run / "freeze_payload.json"), "source_sha256": source_hashes,
                    "input_sha256": {"R03_manifest": freeze_payload["prior_GR3_manifest_sha256"],
                                     "segment_roles": digest(roles_path), "replay_evaluation": digest(method_path)},
                    "seed": seed, "git_head": git_head, "git_dirty": git_dirty,
                    "split_reference_calibration_lineage": "T_R04_splits.csv; T_R04_lineage.csv; actual row IDs deferred to real R05/R06 execution",
                    "environment": environment,
                    "output_sha256": {str(p.relative_to(run)): digest(p) for p in run.rglob("*") if p.is_file() and p.name != "manifest.json"}}
        write_json(run / "manifest.json", manifest)
        print(run)
        if status != "PASS":
            raise RuntimeError("GR4 technical gate blocked; see run logs")
    except Exception as exc:
        (run / "failure.txt").write_text(repr(exc) + "\n")
        raise


if __name__ == "__main__":
    main()
