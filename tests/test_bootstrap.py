"""S00 invariants, including an actual fresh Jupyter kernel."""

import json
import os
from pathlib import Path
import subprocess
import sys

import nbformat
import pytest

from valid_point.provenance import (
    CONFIG_FIELDS, MANIFEST_FIELDS, execute_notebook, export_table, load_config,
    sha256_bytes, validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def test_identical_bytes_have_stable_sha256_and_changed_bytes_do_not():
    assert sha256_bytes(b"same bytes") == sha256_bytes(bytes.fromhex("73616d65206279746573"))
    assert sha256_bytes(b"same bytes") != sha256_bytes(b"same byteS")


def test_bootstrap_config_rejects_invalid_or_research_stage(tmp_path):
    valid = load_config(ROOT / "configs/bootstrap.json")
    assert set(valid) == CONFIG_FIELDS
    for mutation in ({"seed": -1}, {"seed": True}, {"stage": "S01"},
                     {"deadline": {"value": 50, "unit": "ms"}},
                     {"research_results": "success"}):
        path = tmp_path / "invalid.json"
        path.write_text(json.dumps({**valid, **mutation}), encoding="utf-8")
        with pytest.raises(ValueError):
            load_config(path)


def test_manifest_required_fields_and_research_boundary():
    manifest = {key: {"value": "present"} for key in MANIFEST_FIELDS}
    manifest.update({"stage": "S00", "run_id": "example", "started_utc": "now",
                     "finished_utc": "later", "exact_command": "python run",
                     "executed_notebook": "executed.ipynb", "gate": "gate.md",
                     "failures": [], "research_status": {"measurements": "not run", "results": "not run"}})
    validate_manifest(manifest)
    for missing in MANIFEST_FIELDS:
        broken = dict(manifest)
        del broken[missing]
        with pytest.raises(ValueError):
            validate_manifest(broken)
    with pytest.raises(ValueError):
        validate_manifest({**manifest, "research_status": {"measurements": "run", "results": "not run"}})


def test_missing_provenance_rejected_before_file_write(tmp_path):
    with pytest.raises(ValueError, match="provenance"):
        export_table([{"item": "not science"}], "T00_probe", tmp_path, {})
    assert list(tmp_path.iterdir()) == []


def test_fresh_kernel_from_repository_without_previous_state(tmp_path):
    notebook = nbformat.v4.new_notebook(cells=[
        nbformat.v4.new_code_cell("assert 'prior_hidden_state' not in globals()\nprior_hidden_state = 17"),
        nbformat.v4.new_code_cell("import os, sys, valid_point\n"
                                  "assert os.getcwd() == " + repr(str(ROOT)) + "\n"
                                  "assert valid_point.__file__.startswith(" + repr(str(ROOT / "src")) + ")\n"
                                  "print(sys.executable, prior_hidden_state)"),
    ])
    source = tmp_path / "source.ipynb"
    nbformat.write(notebook, source)
    for index in range(2):
        destination = tmp_path / f"executed_{index}.ipynb"
        execute_notebook(source, destination, ROOT)
        result = nbformat.read(destination, as_version=4)
        assert [cell.execution_count for cell in result.cells] == [1, 2]
        assert "17" in result.cells[1].outputs[0].text


def test_import_has_no_research_or_download_side_effect(tmp_path):
    probe = ("import sys,valid_point; "
             "assert not any(name in sys.modules for name in "
             "('requests','torch','open3d','matplotlib','nbclient')); "
             "print(valid_point.__file__)")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run([sys.executable, "-c", probe], cwd=tmp_path, env=env,
                            text=True, capture_output=True, check=True)
    assert str(ROOT / "src" / "valid_point") in result.stdout
    assert list(tmp_path.iterdir()) == []
