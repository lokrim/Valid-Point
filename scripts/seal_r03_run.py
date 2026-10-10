"""Freeze the reviewed R03 evidence bundle after all repairs and checks."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import tarfile
from io import BytesIO

from valid_point.attacks.manifests import file_sha256


ROOT=Path(__file__).resolve().parents[1]
SOURCE_FILES=(
    "src/valid_point/io/mixed_signals.py", "src/valid_point/replay.py",
    "src/valid_point/evidence/density.py", "src/valid_point/evidence/temporal_geometry.py",
    "src/valid_point/attacks/__init__.py", "src/valid_point/attacks/overlays.py",
    "src/valid_point/attacks/manifests.py", "src/valid_point/temporal.py",
    "src/valid_point/development_scores.py", "scripts/replay_development.py",
    "scripts/check_r03_boundary.py", "scripts/summarize_r03_evidence.py",
    "scripts/export_r03_records.py",
    "scripts/repair_r03_rearrangement.py", "scripts/validate_r03_run.py",
    "scripts/seal_r03_run.py", "configs/development_replay.json",
    "notebooks/R03_replay_temporal.ipynb", "tests/test_overlays.py",
    "tests/test_temporal.py", "tests/test_replay_isolation.py",
    "planning/README.md", "planning/01_research_contract.md",
    "planning/02_data_protocol.md", "planning/03_phase1_evidence.md",
    "planning/06_attack_simulation.md", "planning/temporal_spec.md",
    "planning/07_validation.md", "planning/08_notebooks.md",
    "planning/history.md", "planning/progressplan.md", "planning/checklist.md",
    "pyproject.toml", "requirements.lock")


def main(run: Path):
    if (run/"manifest_finalized.marker").exists() and not (run/"review_snapshot/manifest.json").exists():
        raise FileExistsError("R03 bundle is already sealed without a preserved review snapshot")
    prior=json.loads((run/"manifest.json").read_text())
    validation=json.loads((run/"validation.json").read_text())
    if not validation["technical_pass"] or validation["full_tests"]!=108:
        raise RuntimeError("final validation/test gate not ready")
    cfg=json.loads((run/"config.json").read_text())
    # Retain the required short names and provide fully qualified export aliases.
    names=("attempts","roundtrip","state_checks","references","calibration",
           "episode_flow","movement","paired_effects","history","raw_observations",
           "clean_raw_records","normalized_factors","instantaneous_decisions",
           "temporal_states","alarm_decisions","zero_controls","validation")
    for name in names:
        for ext in ("csv","md"):
            source=run/f"T_R03_{name}.{ext}"
            if not source.exists(): raise FileNotFoundError(source)
            target=run/f"T_R03_{name}_D_G_EWMA_mini_7_development_{run.name}.{ext}"
            shutil.copy2(source,target)
    for name in ("geometry","timelines"):
        for ext in ("png","svg","pdf"):
            source=run/f"F_R03_{name}.{ext}"
            target=run/f"F_R03_{name}_D_G_EWMA_mini_7_development_{run.name}.{ext}"
            shutil.copy2(source,target)
    snapshot=run/"source_snapshot.tar.gz"
    with tarfile.open(snapshot,"w:gz") as tar:
        for relative in sorted(SOURCE_FILES):
            data=(ROOT/relative).read_bytes()
            info=tarfile.TarInfo(relative)
            info.size=len(data); info.mode=0o644; info.mtime=0
            tar.addfile(info,BytesIO(data))
    import numpy, matplotlib, nbformat, nbclient, pytest
    original_environment=json.loads((run/"environment.json").read_text())
    env={"python":sys.version,"platform":platform.platform(),"numpy":numpy.__version__,
         "matplotlib":matplotlib.__version__,"nbformat":nbformat.__version__,
         "nbclient":nbclient.__version__,"pytest":pytest.__version__,
         "runner_wall_s_before_repairs":original_environment["wall_s"],
         "runner_cpu_s_before_repairs":original_environment["cpu_s"],
         "runner_peak_rss_bytes":original_environment["peak_rss_bytes"],
         "repair_time_and_peak_rss":"not instrumented separately; see execution_repair.log",
         "free_disk_bytes_at_seal":shutil.disk_usage(ROOT).free,
         "run_dir_bytes_at_seal_before_manifest":sum(p.stat().st_size for p in run.rglob("*") if p.is_file()),
         "peak_disk_bytes":"not instrumented; one active derived episode at a time"}
    (run/"environment_final.json").write_text(json.dumps(env,indent=2)+"\n")
    gate=(
        "# GR3 — real-cloud development replay and temporal gate\n\n"
        "Technical status: **PASS** after the documented rearrangement correction and fresh-kernel notebook repair. "
        "Scientific status: **development-only and uncalibrated**. No alarm effectiveness, false-alarm rate, delay, recovery or generalization is estimated.\n\n"
        "## Executed scope\n\n"
        "mini_7 first 25 acquisition seconds: 1,250 clean production-read PCD events across five streams and four principals. "
        "One middle-severity sustained episode for each of five families, one displacement burst, one benign coordinate-noise control, "
        "and one in-memory calibration/pose-availability timing control. Five zero-severity identity writer/reloader controls. "
        "The scorer/state saw no schedule, evaluator labels, masks, GT boxes, clean shadow or outcomes. Attacked G used attacked-arm history.\n\n"
        "## Technical evidence\n\n"
        "- 641 corrected/demonstration derived PCDs accepted by the clean production reader; all original and 1,000 honest companion PCD hashes unchanged. "
        "Five real PCD identity round trips had zero maximum float32 field error (declared tolerance 1e-6).\n"
        "- Rearrangement preserved every valid D-cell count; 5,785 selected rows had no valid constrained move and remained unchanged. "
        "The first invalid outside-cell execution is retained under `protocol_deviation/`, separate from corrected evidence.\n"
        "- Elapsed-time EWMA tau=1 s, g_reset=0.5 s, ten-update and 3*tau warm-up; clean source cadence is about 0.1 s and `003` D first became ready near 3 s. "
        "Duplicate/reversed time, missing hold/reset, checkpoint, state isolation and prefix tests pass.\n"
        "- Real mini_7 changed/withheld evaluator files left 180 scores and complete temporal state identical; no evaluator file was read, "
        "and the deliberate leaky control failed invariance. Malicious-arm prefixes and all honest companion scores/state match clean replay.\n"
        "- Full regression: 108 passed. The final R03 notebook executed five code cells top-to-bottom in a fresh kernel. "
        "Distinct normalized, instantaneous, temporal and alarm ledgers were exported with source hashes. "
        "PDF/SVG/PNG native/common-top geometry and timeline figures were visually checked for units, common bounds and failure visibility.\n\n"
        "## Reference and scientific limits\n\n"
        "First-10-second real clean mini_7 rows yield 171 supported exploratory contexts of 190 (>=50 distinct cloud rows and positive scale). "
        "`004` G lacks support and remains unknown. The later [10,25) clean block has fewer than 200 known rows per stream/arm; "
        "memoryless and temporal thresholds and every alarm are null. mini_7 is one contiguous scene; internal time blocks are not independent calibration. "
        "The final >=200 rows across >=2 reference segments and distinct calibration-segment rules are unchanged.\n\n"
        "Development D-only `003` paired mean conformity differences (attacked minus clean) include random removal +0.0288, localized removal 0, "
        "displacement -0.1257, rearrangement 0 and addition -0.1586; benign noise is -0.1611. These are descriptive, "
        "unthresholded traces and do not identify attack intent. Post-offset G differences can reflect contaminated attacked history; no recovery is assumed.\n\n"
        "## Failure and provenance\n\n"
        "The earlier interrupted run is `../20261010T152207Z-R03/`; the invalid first rearrangement execution, sandbox notebook failure, "
        "distinct-cloud support verification and figure repair are retained in `execution_repair.log`, `protocol_deviation/`, "
        "`notebook_error.txt` and earlier executed-notebook copies. A deterministic 10,000,000 candidate-pair budget yields unknown G on exhaustion; "
        "no clean event exhausted it. The timing control delays modeled pose availability by 10 ms; original source stamps are unchanged.\n\n"
        "See `manifest.json`, `validation.json`, `boundary_isolation.json`, `prediction_seal.json`, `T_R03_attempts.csv`, "
        "`T_R03_roundtrip.csv`, `T_R03_state_checks.csv`, `T_R03_clean_raw_records.csv`, `T_R03_raw_observations.csv`, "
        "`T_R03_normalized_factors.csv`, `T_R03_instantaneous_decisions.csv`, `T_R03_temporal_states.csv`, `T_R03_alarm_decisions.csv`, "
        "`T_R03_history.csv`, `F_R03_geometry.png`, `F_R03_timelines.png`, "
        "`R03_replay_temporal.executed.ipynb` and `test_results_full.xml`. Stop at GR3. No R04, C0–C3 or H execution.\n\n"
        "Regeneration from current source: `PYTHONPATH=src .venv/bin/python scripts/replay_development.py`; then run the fresh R03 notebook "
        "with local kernel access if sandbox loopback is restricted, run the full tests and `scripts/validate_r03_run.py`, and seal a reviewed run. "
        "The preserved invalid first attempt is historical and need not be reproduced to regenerate the corrected demonstration.\n")
    (run/"gate.md").write_text(gate)
    marker=run/"manifest_finalized.marker"
    marker.write_text(datetime.now(timezone.utc).isoformat()+"\n")
    source_hashes={name:file_sha256(ROOT/name) for name in SOURCE_FILES}
    outputs={str(path.relative_to(run)):file_sha256(path) for path in run.rglob("*")
             if path.is_file() and path.name!="manifest.json"}
    manifest={"run_id":run.name,"stage":"R03","status":"PASS_TECHNICAL_DEVELOPMENT_ONLY",
              "sealed_at_utc":datetime.now(timezone.utc).isoformat(),
              "config_sha256":file_sha256(run/"config.json"),"seed":cfg["seed"],
              "source_sha256":source_hashes,"source_snapshot_sha256":file_sha256(snapshot),
              "source_snapshot_files":list(SOURCE_FILES),
              "input_sha256":prior["input_sha256"],"pose_csv_sha256":prior["pose_csv_sha256"],
              "archive_sha256":cfg["archive_sha256"],"split_lineage":cfg["split_lineage"],
              "reference_id":"R03.exploratory.mini_7.v1","reference_lineage":"T_R03_references.csv: actual first [0,10) s clean cloud IDs; one segment",
              "calibration_id":None,"calibration_lineage":"T_R03_calibration.csv: subsequent clean [10,25) s; <200 known, threshold unavailable",
              "prediction_seal_sha256":file_sha256(run/"prediction_seal.json"),
              "boundary_sha256":file_sha256(run/"boundary_isolation.json"),
              "validation_sha256":file_sha256(run/"validation.json"),
              "git_head":subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip(),
              "git_dirty":subprocess.run(["git","status","--short"],cwd=ROOT,capture_output=True,text=True).stdout,
              "output_sha256":outputs}
    (run/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("sealed",run,"outputs",len(outputs),"source files",len(source_hashes))


if __name__=="__main__":
    main(Path(sys.argv[1]).resolve())
