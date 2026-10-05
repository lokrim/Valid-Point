"""S00 provenance, structural exports, and fresh notebook execution.

No research computation, data acquisition, or package installation occurs here.
Optional notebook/plot packages are imported only by the functions that need them.
"""

from __future__ import annotations

import csv
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
import tomllib
from typing import Any


CONFIG_FIELDS = {
    "schema_version", "stage", "track", "segment", "split_role", "seed",
    "rng_scheme", "deadline", "time_mapping", "frame_id", "transform_id",
    "reference_lineage", "calibration_lineage", "policy_id", "attack_id",
    "research_measurements", "research_results",
}
MANIFEST_FIELDS = {
    "manifest_schema_version", "stage", "stage_version", "run_id",
    "started_utc", "finished_utc", "exact_command", "configuration",
    "seeds", "source", "environment", "data_lineage", "decision_context",
    "inputs", "outputs", "failures", "tests", "executed_notebook",
    "gate", "research_status",
}
SOURCE_PATHS = (
    "pyproject.toml", "requirements.lock", "configs/bootstrap.json",
    "src/valid_point/__init__.py", "src/valid_point/provenance.py",
    "scripts/execute_notebooks.py", "tests/test_bootstrap.py",
    "notebooks/00_bootstrap.ipynb",
)
BOOTSTRAP_PACKAGES = ("ipykernel", "nbclient", "nbformat", "matplotlib", "pytest")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def write_json_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(json_bytes(value))


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or set(config) != CONFIG_FIELDS:
        raise ValueError("bootstrap config fields differ from the S00 schema")
    expected = {
        "schema_version": "s00.bootstrap.v1", "stage": "S00",
        "track": "infrastructure", "segment": "none",
        "research_measurements": "not run", "research_results": "not run",
        "reference_lineage": "not run", "calibration_lineage": "not run",
        "policy_id": "not run", "attack_id": "not run",
    }
    if any(config[key] != value for key, value in expected.items()):
        raise ValueError("bootstrap config requests a research stage or invalid state")
    if type(config["seed"]) is not int or config["seed"] < 0:
        raise ValueError("seed must be a nonnegative integer")
    deadline = config["deadline"]
    if deadline != {"value": None, "unit": "not applicable: no sender/frame decision"}:
        raise ValueError("S00 has no sender/frame deadline")
    for field in ("split_role", "rng_scheme", "time_mapping", "frame_id", "transform_id"):
        if not isinstance(config[field], str) or not config[field].startswith("not applicable:"):
            raise ValueError(f"{field} must explain why it is not applicable")
    return config


def source_inventory(root: Path) -> tuple[list[dict[str, str]], str]:
    entries = []
    digest = hashlib.sha256()
    for name in SOURCE_PATHS:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(f"required source file missing: {name}")
        content = path.read_bytes()
        file_hash = sha256_bytes(content)
        entries.append({"path": name, "sha256": file_hash})
        digest.update(name.encode() + b"\0" + content + b"\0")
    return entries, digest.hexdigest()


def format_source_tree(entries: list[dict[str, str]]) -> str:
    """Render the bounded source inventory as a readable directory tree."""
    lines = ["valid-point/"]
    directories: set[str] = set()
    for entry in entries:
        parts = Path(entry["path"]).parts
        for depth in range(1, len(parts)):
            directory = "/".join(parts[:depth])
            if directory not in directories:
                lines.append("  " * depth + parts[depth - 1] + "/")
                directories.add(directory)
        lines.append("  " * len(parts) + parts[-1])
    return "\n".join(lines)


def environment_inventory() -> dict[str, Any]:
    import valid_point

    packages = {}
    for name in BOOTSTRAP_PACKAGES:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "missing"
    return {
        "interpreter": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "package_origin": str(Path(valid_point.__file__).resolve()),
        "package_version": tomllib.loads(
            (Path(valid_point.__file__).resolve().parents[2] / "pyproject.toml").read_text(encoding="utf-8")
        )["project"]["version"],
        "packages": packages,
    }


def validate_provenance(provenance: dict[str, str]) -> None:
    required = {"run_id", "stage", "track", "segment", "config_sha256", "source_sha256", "notebook_section"}
    if not isinstance(provenance, dict) or not required.issubset(provenance):
        raise ValueError("missing required export provenance")
    if any(not isinstance(provenance[key], str) or not provenance[key].strip() for key in required):
        raise ValueError("empty required export provenance")


def output_stem(name: str, provenance: dict[str, str]) -> str:
    validate_provenance(provenance)
    if not name.replace("_", "").isalnum():
        raise ValueError("output name must be alphanumeric with underscores")
    return "_".join((name, provenance["stage"], provenance["track"],
                     provenance["segment"], provenance["run_id"]))


def export_table(rows: list[dict[str, str]], name: str, report_dir: Path,
                 provenance: dict[str, str]) -> list[Path]:
    """Export a complete small structural table and a provenance sidecar."""
    stem = output_stem(name, provenance)
    if not rows or not all(set(row) == set(rows[0]) for row in rows):
        raise ValueError("table rows must be nonempty with identical fields")
    paths = [report_dir / f"{stem}.{ext}" for ext in ("csv", "md", "provenance.json")]
    if any(path.exists() for path in paths):
        raise FileExistsError(stem)
    report_dir.mkdir(parents=True, exist_ok=True)
    with paths[0].open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    headers = list(rows[0])
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines += ["| " + " | ".join(str(row[key]).replace("|", "\\|").replace("\n", " ") for key in headers) + " |" for row in rows]
    paths[1].write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json_new(paths[2], {**provenance, "name": name, "row_count": len(rows),
                              "outputs": {path.name: sha256_file(path) for path in paths[:2]}})
    return paths


def structure_figure(report_dir: Path, provenance: dict[str, str]) -> list[Path]:
    """Draw the S00 source/execution/export dependency diagram."""
    stem = output_stem("F00_structure", provenance)
    paths = [report_dir / f"{stem}.{ext}" for ext in ("pdf", "svg", "png", "provenance.json")]
    if any(path.exists() for path in paths):
        raise FileExistsError(stem)
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib.figure import Figure

    report_dir.mkdir(parents=True, exist_ok=True)
    fig = Figure(figsize=(10, 3.1), dpi=160)
    ax = fig.subplots()
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 1)
    ax.axis("off")
    nodes = ("Frozen config\n+ source", "valid_point\nprovenance", "Fresh kernel\nNB00", "Run bundle\n+ reports")
    for index, label in enumerate(nodes):
        ax.text(index + .5, .5, label, ha="center", va="center", fontsize=10,
                bbox={"boxstyle": "round,pad=.6", "facecolor": "#e8f1f8", "edgecolor": "#285a7c"})
        if index < len(nodes) - 1:
            ax.annotate("", xy=(index + 1.21, .5), xytext=(index + .8, .5),
                        arrowprops={"arrowstyle": "->", "color": "#285a7c", "lw": 1.5})
    ax.set_title("F00_structure — S00 execution and export flow; science not run", fontsize=11)
    for path in paths[:3]:
        fig.savefig(path, bbox_inches="tight")
    write_json_new(paths[3], {**provenance, "name": "F00_structure",
                              "outputs": {path.name: sha256_file(path) for path in paths[:3]}})
    return paths


def export_roundtrip(run_dir: Path, provenance: dict[str, str]) -> dict[str, str]:
    """Test tiny non-scientific bytes, then demonstrate missing-provenance rejection."""
    validate_provenance(provenance)
    payload = b"kind,status\nbootstrap_export,ok\n"
    path = run_dir / "non_scientific_roundtrip.csv"
    with path.open("xb") as stream:
        stream.write(payload)
    write_json_new(run_dir / "non_scientific_roundtrip.provenance.json",
                   {**provenance, "sha256": sha256_file(path), "science": "not run"})
    if path.read_bytes() != payload:
        raise AssertionError("non-scientific export round trip failed")
    try:
        export_table([{"check": "missing provenance"}], "T00_forbidden",
                     run_dir, {})
    except ValueError as exc:
        failure = str(exc)
    else:
        raise AssertionError("missing provenance was accepted")
    return {"roundtrip": "pass", "sha256": sha256_file(path),
            "missing_provenance": f"rejected: {failure}"}


def validate_manifest(manifest: dict[str, Any]) -> None:
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_FIELDS:
        raise ValueError("manifest required fields missing or unexpected")
    if manifest["stage"] != "S00" or manifest["research_status"] != {"measurements": "not run", "results": "not run"}:
        raise ValueError("S00 manifest contains an invalid research status")
    for key in ("run_id", "started_utc", "finished_utc", "exact_command", "executed_notebook", "gate"):
        if not isinstance(manifest[key], str) or not manifest[key]:
            raise ValueError(f"manifest {key} is empty")
    for key in ("configuration", "seeds", "source", "environment", "data_lineage",
                "decision_context", "inputs", "outputs", "tests"):
        if not isinstance(manifest[key], dict) or not manifest[key]:
            raise ValueError(f"manifest {key} is empty")
    if not isinstance(manifest["failures"], list):
        raise ValueError("manifest failures must be a list")


def execute_notebook(source: Path, destination: Path, root: Path,
                     extra_env: dict[str, str] | None = None) -> None:
    """Execute an unexecuted notebook in a new Jupyter kernel at repository root."""
    import nbformat
    from nbclient import NotebookClient

    notebook = nbformat.read(source, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == "code" and (cell.get("outputs") or cell.get("execution_count") is not None):
            raise ValueError("source notebook contains generated outputs")
    destination.parent.mkdir(parents=True, exist_ok=True)
    old = {key: os.environ.get(key) for key in (extra_env or {})}
    try:
        os.environ.update(extra_env or {})
        client = NotebookClient(notebook, timeout=120, kernel_name="python3",
                                resources={"metadata": {"path": str(root)}})
        client.execute()
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        nbformat.write(notebook, destination)


def notebook_context() -> tuple[Path, Path, dict[str, Any], dict[str, str]]:
    """Load exact S00 context passed by the runner; fail without it."""
    root_text, run_text = os.environ.get("VP_REPO_ROOT"), os.environ.get("VP_RUN_DIR")
    if not root_text or not run_text:
        raise ValueError("S00 notebook requires runner-provided repository and run paths")
    root, run_dir = Path(root_text).resolve(), Path(run_text).resolve()
    if run_dir.parent != root / "artifacts" or not run_dir.is_dir():
        raise ValueError("invalid S00 run directory")
    config_path = root / "configs/bootstrap.json"
    config = load_config(config_path)
    _, source_hash = source_inventory(root)
    provenance = {"run_id": run_dir.name, "stage": "S00", "track": "infrastructure",
                  "segment": "none", "config_sha256": sha256_file(config_path),
                  "source_sha256": source_hash, "notebook_section": "NB00"}
    return root, run_dir, config, provenance


def bootstrap_tables(root: Path, config: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
    environment = environment_inventory()
    files, source_hash = source_inventory(root)
    env_rows = [
        {"item": "interpreter", "value": environment["interpreter"], "state": "observed"},
        {"item": "python_version", "value": environment["python_version"], "state": "observed"},
        {"item": "platform", "value": environment["platform"], "state": "observed"},
        {"item": "package_origin", "value": environment["package_origin"], "state": "observed"},
        {"item": "package_version", "value": environment["package_version"], "state": "observed"},
    ]
    env_rows += [{"item": f"dependency:{name}", "value": version, "state": "observed"}
                 for name, version in environment["packages"].items()]
    env_rows += [{"item": "decision_unit", "value": "sender/frame/deadline", "state": "not applicable: science not run"},
                 {"item": "deadline", "value": config["deadline"]["unit"], "state": "not applicable"},
                 {"item": "research_measurements", "value": "not run", "state": "not run"},
                 {"item": "research_results", "value": "not run", "state": "not run"}]
    scaffold_rows = [{"path": item["path"], "sha256": item["sha256"], "state": "source present"}
                     for item in files]
    return env_rows, scaffold_rows, source_hash


def git_revision(root: Path) -> dict[str, str]:
    def git(*args: str) -> str:
        result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)
        return result.stdout.strip()
    try:
        return {"commit": git("rev-parse", "HEAD"),
                "dirty": str(bool(git("status", "--porcelain", "--untracked-files=all"))).lower(),
                "remote_url": git("remote", "get-url", "origin") if git("remote") else "not applicable: no remote"}
    except (FileNotFoundError, subprocess.CalledProcessError):
        return {"commit": "not applicable: no Git revision", "dirty": "unknown",
                "remote_url": "not applicable: no remote"}


def bootstrap_run(root: Path) -> Path:
    """Run tests and NB00, then seal a unique local evidence bundle."""
    root = root.resolve()
    config_path = root / "configs/bootstrap.json"
    config = load_config(config_path)
    files, source_hash = source_inventory(root)
    started = utc_now()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "Z-" + secrets.token_hex(4)
    run_dir = root / "artifacts" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    log_lines = [f"start: {started}", f"command: {sys.executable} scripts/execute_notebooks.py",
                 "notebook: notebooks/00_bootstrap.ipynb", "working_directory: repository root"]
    with (run_dir / "config.json").open("xb") as stream:
        stream.write(config_path.read_bytes())
    write_json_new(run_dir / "seeds.json", {"seed": config["seed"], "rng_scheme": config["rng_scheme"]})
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src") + os.pathsep + env.get("PYTHONPATH", "")
    env["MPLCONFIGDIR"] = str(run_dir / "matplotlib_cache")
    test_command = [sys.executable, "-m", "pytest", "-q", "tests/test_bootstrap.py"]
    test = subprocess.run(test_command, cwd=root, env=env, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, check=False)
    write_json_new(run_dir / "test_results.json", {"command": test_command, "exit_code": test.returncode,
                                                    "output": test.stdout})
    log_lines += ["tests:", test.stdout, f"test_exit_code: {test.returncode}"]
    notebook_failure = None
    executed_name = "00_bootstrap.executed.ipynb"
    old_environment = {key: os.environ.get(key) for key in ("PYTHONPATH", "MPLCONFIGDIR")}
    try:
        os.environ["PYTHONPATH"] = env["PYTHONPATH"]
        os.environ["MPLCONFIGDIR"] = env["MPLCONFIGDIR"]
        execute_notebook(root / "notebooks/00_bootstrap.ipynb", run_dir / executed_name,
                         root, {"VP_REPO_ROOT": str(root), "VP_RUN_DIR": str(run_dir)})
        log_lines.append("notebook_execution: passed; new kernel")
    except Exception as exc:  # retain failed execution evidence
        notebook_failure = f"{type(exc).__name__}: {exc}"
        log_lines.append(f"notebook_execution: failed: {notebook_failure}")
    finally:
        for key, value in old_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    passed = test.returncode == 0 and notebook_failure is None
    failures = []
    if test.returncode:
        failures.append(f"bootstrap tests failed with exit code {test.returncode}")
    if notebook_failure:
        failures.append(notebook_failure)
    gate = "PASS — G1 infrastructure portion" if passed else "BLOCKED — G1 infrastructure portion"
    gate_text = (f"# S00 gate\n\n{gate}\n\nResearch measurements/results: **not run**. "
                 f"S01 and the scientific part of G1 remain pending explicit invocation.\n\n"
                 f"Tests: {'pass' if test.returncode == 0 else 'fail'}; "
                 f"fresh-kernel NB00: {'pass' if notebook_failure is None else 'fail'}.\n\n"
                 f"Failures: {failures or 'none'}\n")
    (run_dir / "gate.md").write_text(gate_text, encoding="utf-8")
    finished = utc_now()
    log_lines.append(f"finish: {finished}")
    (run_dir / "execution.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    suffix = f"S00_infrastructure_none_{run_id}"
    report_files = sorted(path for base in (root / "reports/tables", root / "reports/figures")
                          for path in base.glob(f"*{suffix}*") if path.is_file())
    output_files = sorted(path for path in run_dir.rglob("*") if path.is_file()) + report_files
    manifest = {
        "manifest_schema_version": "s00.manifest.v1", "stage": "S00", "stage_version": "1",
        "run_id": run_id, "started_utc": started, "finished_utc": finished,
        "exact_command": f"{sys.executable} scripts/execute_notebooks.py",
        "configuration": {"path": "configs/bootstrap.json", "sha256": sha256_file(config_path),
                          "bytes_sha256": sha256_file(run_dir / "config.json"), "value": config},
        "seeds": {"path": "seeds.json", "value": config["seed"], "rng_scheme": config["rng_scheme"]},
        "source": {**git_revision(root), "snapshot_sha256": source_hash, "files": files,
                   "license": "not applicable: no research source data"},
        "environment": environment_inventory(),
        "data_lineage": {"source_url": "not applicable: no research data", "source_revision": "not run",
                         "archive_sha256": "not run", "member_sha256": "not run",
                         "cloud_sha256": "not run", "reference": "not run", "calibration": "not run"},
        "decision_context": {key: config[key] for key in ("track", "segment", "split_role", "deadline", "time_mapping",
                                                        "frame_id", "transform_id", "policy_id", "attack_id")},
        "inputs": {item["path"]: item["sha256"] for item in files},
        "outputs": {str(path.relative_to(root)): sha256_file(path) for path in output_files},
        "failures": failures,
        "tests": {"command": test_command, "exit_code": test.returncode, "report": "test_results.json"},
        "executed_notebook": executed_name if (run_dir / executed_name).exists() else "not produced: execution failure",
        "gate": "gate.md", "research_status": {"measurements": "not run", "results": "not run"},
    }
    validate_manifest(manifest)
    write_json_new(run_dir / "manifest.json", manifest)
    # The evidence bundle is sealed after the manifest and all output hashes exist.
    for path in run_dir.rglob("*"):
        if path.is_file():
            path.chmod(0o444)
    for path in sorted((path for path in run_dir.rglob("*") if path.is_dir()), reverse=True):
        path.chmod(0o555)
    run_dir.chmod(0o555)
    return run_dir
