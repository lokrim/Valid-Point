"""Execute S04 tests and NB04 in a fresh kernel; seal the negative G3 result."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import secrets
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from valid_point.provenance import execute_notebook, git_revision, sha256_file, utc_now, write_json_new


NOTEBOOK = "04_gt_free_oracle_gap"


def main() -> int:
    config_path = ROOT / "configs/spatial_tracks.json"
    config = json.loads(config_path.read_text())
    tracks = ("gt_free", "oracle_box")
    seed_groups = {
        f"{track}_{role}": tuple(config["splits"][track][f"{role}_seeds"])
        for track in tracks for role in ("reference", "calibration")
    }
    seed_groups.update({f"{track}_test": (config["splits"][track]["test_seed"],) for track in tracks})
    flattened = [seed for values in seed_groups.values() for seed in values]
    if len(flattened) != len(set(flattened)):
        raise ValueError("track reference/calibration/test seeds must be disjoint")

    sources = sorted(set(
        [path for folder in ("src", "tests", "configs", "scripts")
         for path in (ROOT / folder).rglob("*") if path.suffix in (".py", ".json")]
        + [ROOT / "notebooks" / f"{NOTEBOOK}.ipynb"]
        + [ROOT / "planning/03_phase1_evidence.md", ROOT / "planning/09_decisions_and_gates.md",
           ROOT / "planning/08_notebooks.md", ROOT / "pyproject.toml", ROOT / "requirements.lock",
           ROOT / ".gitignore"]
    ))
    source_hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in sources}
    digest = hashlib.sha256()
    for path in sources:
        digest.update(str(path.relative_to(ROOT)).encode() + b"\0" + path.read_bytes() + b"\0")
    source_hash = digest.hexdigest()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4)
    run = ROOT / "artifacts" / run_id
    run.mkdir(parents=True, exist_ok=False)
    started = utc_now()
    failures: list[str] = []
    log = [f"start: {started}", f"command: {sys.executable} scripts/compare_spatial_tracks.py"]

    for path in sources:
        destination = run / "source" / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())
    (run / "config.json").write_bytes(config_path.read_bytes())
    write_json_new(run / "seeds.json", {
        **{name: list(values) for name, values in seed_groups.items()},
        "rng_scheme": "deterministic constructed geometry; no random generator",
    })

    environment = {**os.environ, "PYTHONPATH": str(ROOT / "src"),
                   "MPLCONFIGDIR": str(run / "matplotlib_cache")}
    command = [sys.executable, "-m", "pytest", "-q", "tests", "--junitxml=" + str(run / "tests.xml")]
    test_result = subprocess.run(command, cwd=ROOT, env=environment, text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    write_json_new(run / "test_results.json", {
        "command": command, "exit_code": test_result.returncode, "output": test_result.stdout,
    })
    log += ["tests:", test_result.stdout]
    if test_result.returncode:
        failures.append("test suite failed")

    notebooks = []
    old = {key: os.environ.get(key) for key in ("PYTHONPATH", "MPLCONFIGDIR")}
    try:
        os.environ["PYTHONPATH"] = environment["PYTHONPATH"]
        os.environ["MPLCONFIGDIR"] = environment["MPLCONFIGDIR"]
        log.append(f"{utc_now()} fresh kernel start: {NOTEBOOK}")
        try:
            execute_notebook(
                ROOT / "notebooks" / f"{NOTEBOOK}.ipynb",
                run / f"{NOTEBOOK}.executed.ipynb", ROOT,
                {"VP_REPO_ROOT": str(ROOT), "VP_RUN_DIR": str(run),
                 "VP_SOURCE_SHA256": source_hash},
            )
            notebooks.append(f"{NOTEBOOK}.executed.ipynb")
            log.append(f"{utc_now()} notebook PASS: {NOTEBOOK}")
        except Exception as exc:
            failures.append(f"{NOTEBOOK}: {type(exc).__name__}: {exc}")
            log.append(f"{utc_now()} notebook FAIL: {failures[-1]}")
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    result_path = run / "spatial_gap_result.json"
    if result_path.exists():
        result = json.loads(result_path.read_text())
        if result["gate"]["technical"] != "PASS":
            failures.append("notebook technical gate failed")
        if result["gate"]["G3"] != "FAIL_NEGATIVE_RESULT":
            failures.append("G3 negative result was not retained")
        if not all(result["contract_checks"].values()):
            failures.append("one or more spatial contract checks failed")
    else:
        result = None
        failures.append("spatial gap evidence missing")
    if any(sha256_file(ROOT / name) != expected for name, expected in source_hashes.items()):
        failures.append("source changed during execution")
    if subprocess.run(["git", "check-ignore", "-q", str(run / "source")], cwd=ROOT).returncode:
        failures.append("source snapshot not Git-ignored")

    technical = "PASS" if not failures else "FAIL"
    stage_suffix = f"_S04_paired_constructed_gap_cases_{run_id}"
    table_link = f"../../reports/tables/T04_gap_cases{stage_suffix}.md"
    figure_link = f"../../reports/figures/F04_oracle_gap{stage_suffix}.png"
    gate = (
        "# S04 G3 GT-free viability gate\n\n"
        f"**Technical execution: {technical}. G3: "
        f"{'FAIL — negative scientific result; operational readiness and real-policy claims are blocked.' if technical == 'PASS' else 'BLOCKED — technical execution failed.'}**\n\n"
        f"Tests exit: {test_result.returncode}; fresh notebooks: {len(notebooks)}/1. "
        "GT-free and oracle-box references/calibrations use disjoint seeds and independent bundles.\n\n"
        "The constructed cases expose GT-free misses for a box split across tiles, outside-ROI addition, "
        "and count-preserving rearrangement; false alarms occur for a unique honest view and changing benign "
        "content; an absent packet abstains. Fixed tiles do detect concentrated in-ROI additions and an empty-"
        "region ghost. This is a valid negative result on deterministic fixtures, not empirical sensor validity. "
        "T is conformity, not an honesty probability. The ego-only proposal scorer is deferred; proposal failure "
        "states remain visible and do not affect GT-free decisions. No detector, external data, policy, or later "
        "stage was executed.\n\n"
        f"Failures: {failures or 'none'}.\n\n"
        "Evidence: [manifest](manifest.json), [tests](test_results.json), "
        "[execution log](execution.log), [executed NB04](04_gt_free_oracle_gap.executed.ipynb), "
        f"[T04_gap_cases]({table_link}), [F04_oracle_gap]({figure_link}), "
        "[result](spatial_gap_result.json).\n"
    )
    (run / "gate.md").write_text(gate)
    finished = utc_now()
    log += [f"finish: {finished}", f"technical gate: {technical}",
            "G3: FAIL_NEGATIVE_RESULT" if technical == "PASS" else "G3: BLOCKED"]
    (run / "execution.log").write_text("\n".join(log) + "\n")

    reports = sorted(path for folder in ("tables", "figures")
                     for path in (ROOT / "reports" / folder).glob("*" + run_id + "*"))
    outputs = sorted(path for path in run.rglob("*") if path.is_file()) + reports
    packages = {}
    for name in ("numpy", "matplotlib", "pytest", "nbformat", "nbclient", "ipykernel"):
        packages[name] = importlib.metadata.version(name)
    manifest = {
        "manifest_schema_version": "s04.manifest.v1", "stage": "S04", "stage_version": "1",
        "run_id": run_id, "started_utc": started, "finished_utc": finished,
        "exact_command": f"{sys.executable} scripts/compare_spatial_tracks.py",
        "configuration": {"source": "configs/spatial_tracks.json", "sha256": sha256_file(run / "config.json"),
                          "value": config},
        "seeds": {"file": "seeds.json", "sha256": sha256_file(run / "seeds.json"),
                  **{name: list(values) for name, values in seed_groups.items()}},
        "source": {**git_revision(ROOT), "snapshot_sha256": source_hash, "files": source_hashes,
                   "snapshot_path": "source", "source_url": "local deterministic constructed spatial fixtures",
                   "source_revision": "s04.spatial_tracks.v1", "license": "project source; no external dataset"},
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "executable": sys.executable, "packages": packages},
        "decision_context": {"track": "paired gt_free/oracle_box", "segment": "constructed_gap_cases",
                             "decision_unit": config["decision_unit"],
                             "deadline_ns": config["decision"]["deadline_ns"],
                             "region_authority": {"gt_free": "receiver", "oracle_box": "evaluator"}},
        "data_lineage": {"split_track": seed_groups, "references": "spatial_gap_result.json#references",
                         "calibrations": "spatial_gap_result.json#calibrations",
                         "input_fixture_config_sha256": sha256_file(run / "config.json"),
                         "archive": "not applicable; no external data"},
        "inputs": {"config.json": sha256_file(run / "config.json"),
                   "seeds.json": sha256_file(run / "seeds.json")},
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in outputs},
        "failures": failures, "tests": {"exit_code": test_result.returncode,
                                         "report": "test_results.json", "junit": "tests.xml"},
        "executed_notebooks": notebooks, "gate": "gate.md",
        "research_status": {"technical": technical,
                            "G3": "FAIL_NEGATIVE_RESULT" if technical == "PASS" else "BLOCKED",
                            "operational_readiness": "blocked", "future_policy": "not run"},
    }
    write_json_new(run / "manifest.json", manifest)
    for name, expected in manifest["outputs"].items():
        if sha256_file(ROOT / name) != expected:
            raise RuntimeError("output hash mismatch: " + name)
    for path in outputs + [run / "manifest.json"]:
        path.chmod(0o444)
    for path in sorted((path for path in run.rglob("*") if path.is_dir()), reverse=True):
        path.chmod(0o555)
    run.chmod(0o555)
    print(run)
    print(gate)
    return 0 if technical == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
