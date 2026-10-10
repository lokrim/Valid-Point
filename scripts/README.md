# Stage runners

**Current R sequence:** invoke one stage at a time. R01's completed intake is documented by [GR1](../artifacts/20261008T192922Z-R01/gate.md). R02 is `.venv/bin/python scripts/inspect_causal_factors.py`, with [config](../configs/causal_factors.json) and [notebook](../notebooks/R02_causal_factors.ipynb). It runs only the bounded authorized `mini_7` raw-factor experiment and stops at GR2. Jupyter fresh kernels require local socket access. The runner saves a unique ignored run directory and never launches R03 or another stage.

**Historical S runners:** `execute_notebooks.py` (S00), `show_synthetic_scene.py` (S01), `measure_synthetic.py` (S02), `fit_and_score.py` (S03), and `compare_spatial_tracks.py` (S04) reproduce constructed/infrastructure work at its original scope. Do not use their output or `gt_free.score_clouds` as an R02 eligibility or inference entry point. See [audit](../planning/evidence_audit.md) for the exact limits, including S04's incomplete boundary test.

Run R02 tests alone with `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_replay.py tests/test_causal_factors.py`. The runner also executes the full `tests/` suite and stores JUnit and log files. Do not use an unqualified repository-wide pytest collection: historical artifact snapshots may duplicate test modules.
