"""Run S01 tests and NB01 from a fresh kernel; seal a new local evidence bundle."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.metadata
import os
from pathlib import Path
import platform
import secrets
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from valid_point.provenance import (execute_notebook, git_revision, sha256_file,
                                    utc_now, write_json_new)  # noqa: E402
from valid_point.synthetic import load_synthetic_config  # noqa: E402


SOURCE_FILES = (
    "pyproject.toml", "configs/synthetic.json", "src/valid_point/__init__.py",
    "src/valid_point/contracts.py", "src/valid_point/synthetic.py",
    "src/valid_point/io/__init__.py", "src/valid_point/io/pointcloud.py",
    "src/valid_point/provenance.py", "scripts/show_synthetic_scene.py",
    "tests/test_contracts.py", "tests/test_synthetic.py", "tests/test_pointcloud_io.py",
    "notebooks/01_synthetic_scenes.ipynb",
)


def source_snapshot() -> tuple[dict[str, str], str]:
    hashes = {name: sha256_file(ROOT / name) for name in SOURCE_FILES}
    digest = hashlib.sha256()
    for name in SOURCE_FILES:
        digest.update(name.encode() + b"\0" + (ROOT / name).read_bytes() + b"\0")
    return hashes, digest.hexdigest()


def main() -> Path:
    config_path = ROOT / "configs/synthetic.json"
    config = load_synthetic_config(config_path)
    source_hashes, snapshot_hash = source_snapshot()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "Z-" + secrets.token_hex(4)
    run_dir = ROOT / "artifacts" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = utc_now()
    (run_dir / "config.json").write_bytes(config_path.read_bytes())
    write_json_new(run_dir / "seeds.json", {"families": config["seed_families"],
                                            "demonstration_seed": 0, "rng_scheme": config["rng_scheme"]})
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["MPLCONFIGDIR"] = str(run_dir / "matplotlib_cache")
    command = [sys.executable, "-m", "pytest", "-q", "tests/test_contracts.py",
               "tests/test_synthetic.py", "tests/test_pointcloud_io.py"]
    test = subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False)
    write_json_new(run_dir / "test_results.json", {"command": command, "exit_code": test.returncode,
                                                    "output": test.stdout})
    failure = None
    executed = "01_synthetic_scenes.executed.ipynb"
    previous = {key: os.environ.get(key) for key in ("PYTHONPATH", "MPLCONFIGDIR")}
    try:
        os.environ["PYTHONPATH"] = env["PYTHONPATH"]
        os.environ["MPLCONFIGDIR"] = env["MPLCONFIGDIR"]
        execute_notebook(ROOT / "notebooks/01_synthetic_scenes.ipynb", run_dir / executed, ROOT,
                         {"VP_REPO_ROOT": str(ROOT), "VP_RUN_DIR": str(run_dir),
                          "VP_SOURCE_SHA256": snapshot_hash})
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    passed = test.returncode == 0 and failure is None
    failures = ([f"tests exit {test.returncode}"] if test.returncode else []) + ([failure] if failure else [])
    gate_status = "PASS" if passed else "BLOCKED"
    (run_dir / "gate.md").write_text(
        f"# S01 / G1 gate\n\n**{gate_status}** — causal synthetic scene contracts and first visualization.\n\n"
        f"Targeted tests: {'pass' if test.returncode == 0 else 'fail'}; "
        f"NB01 fresh kernel: {'pass' if failure is None else 'fail'}.\n\n"
        "Scope: geometry, causal availability, strict unknowns and reader round trips only. "
        "No score, alarm, attack, quota, reference fit or calibration was run. "
        "Evaluator visibility/target geometry cannot establish a GT-free finding.\n\n"
        f"Failures: {failures or 'none'}\n", encoding="utf-8")
    finished = utc_now()
    (run_dir / "execution.log").write_text(
        f"start: {started}\ncommand: {sys.executable} scripts/show_synthetic_scene.py\n"
        f"tests: {' '.join(command)}\n{test.stdout}\n"
        f"fresh_kernel_notebook: {'passed' if failure is None else failure}\nfinish: {finished}\n",
        encoding="utf-8")
    report_paths = sorted(path for base in (ROOT / "reports/tables", ROOT / "reports/figures")
                          for path in base.glob(f"*{run_id}*") if path.is_file())
    output_paths = sorted(p for p in run_dir.rglob("*") if p.is_file()) + report_paths
    manifest = {
        "manifest_schema_version": "s01.manifest.v1", "stage": "S01", "stage_version": "1",
        "run_id": run_id, "started_utc": started, "finished_utc": finished,
        "exact_command": f"{sys.executable} scripts/show_synthetic_scene.py",
        "configuration": {"source": "configs/synthetic.json", "sha256": sha256_file(config_path),
                          "run_copy_sha256": sha256_file(run_dir / "config.json"), "value": config},
        "seeds": {"source": "seeds.json", "sha256": sha256_file(run_dir / "seeds.json"),
                  "families": config["seed_families"], "demonstration_seed": 0,
                  "rng_scheme": config["rng_scheme"]},
        "source": {**git_revision(ROOT), "snapshot_sha256": snapshot_hash, "files": source_hashes,
                   "source_url": "local generated synthetic geometry", "source_revision": "s01.synthetic.v1",
                   "license": "project source; no external data"},
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "executable": sys.executable,
                        "packages": {name: importlib.metadata.version(name) for name in
                                     ("numpy", "matplotlib", "pytest", "nbformat", "nbclient", "ipykernel")}},
        "data_lineage": {"archive": "not applicable: synthetic", "member": "not applicable: synthetic",
                         "cloud": "run-local canonical JSON; SHA-256 in outputs",
                         "reference": config["reference_lineage"],
                         "calibration": config["calibration_lineage"]},
        "decision_context": {"track": config["track"], "split_role": "development",
                             "segment": config["episode"] + "_0", "deadline_delta_ns": config["deadline_delta_ns"],
                             "time_mapping": config["time_mapping"], "frame_id": 0,
                             "transform_ids": [f"receiver_from_{s}" for s in ("west_low", "west_high", "north")],
                             "policy_id": "not run", "attack_id": "not run"},
        "inputs": source_hashes,
        "outputs": {str(path.relative_to(ROOT)): sha256_file(path) for path in output_paths},
        "failures": failures,
        "tests": {"command": command, "exit_code": test.returncode, "report": "test_results.json"},
        "executed_notebook": executed if (run_dir / executed).exists() else "not produced",
        "gate": "gate.md",
        "research_status": {"scene_contract": "executed" if passed else "blocked",
                            "scores": "not run", "attacks": "not run", "allocation": "not run"},
    }
    write_json_new(run_dir / "manifest.json", manifest)
    for path in run_dir.rglob("*"):
        if path.is_file():
            path.chmod(0o444)
    for path in sorted((p for p in run_dir.rglob("*") if p.is_dir()), reverse=True):
        path.chmod(0o555)
    run_dir.chmod(0o555)
    return run_dir


if __name__ == "__main__":
    result = main()
    print(result)
    print((result / "gate.md").read_text(encoding="utf-8"))
    if "**PASS**" not in (result / "gate.md").read_text(encoding="utf-8"):
        raise SystemExit(1)
