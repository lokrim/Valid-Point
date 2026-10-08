# Valid Point

Valid Point studies whether explainable, ground-truth-free sender conformity
checks can detect specified corruptions in cooperative LiDAR observations and
help allocate bandwidth without unnecessarily excluding honest viewpoints.
The repository is `valid-point`; the Python package is `valid_point`.

**Status: S00 bootstrap executed; science not run.** There are no research
algorithms, datasets, attacks, simulations, or scientific results. The package
has no runtime dependencies and imports from `src/`. The S00-only notebook,
figure and test tools are pinned in `requirements.lock`.

Start with the [planning index](planning/README.md),
[ordered stages](planning/progressplan.md), and
[review decisions](planning/09_decisions_and_gates.md). The
[acceptance checklist](planning/checklist.md) separates visible evidence from
unimplemented work. Future [stage prompts](planning/prompts/README.md) run one
stage at a time and never launch each other.

The design starts with synthetic scenes and ordinary Python functions, shown
in fresh-kernel notebooks. It separates oracle-box research from a required
GT-free inference path. Real-data comparison requires at least four distinct
labeled segments, each held out once. Scores express conformity, not honesty
probabilities or guaranteed usefulness. Negative and unsupported cases belong
in the paper.

| Directory | Purpose |
| --- | --- |
| `src/valid_point/`, `tests/`, `scripts/` | S00 provenance, meaningful checks, small entry point; research computation pending |
| `notebooks/`, `configs/` | S00 fresh-kernel evidence and frozen configuration; later stages pending |
| `planning/` | Method contracts, decisions, provenance, acceptance, staged prompts |
| `data/`, `artifacts/` | Ignored raw inputs and reproducible generated runs |
| `reports/figures/`, `reports/tables/` | Ignored report-ready exports with provenance |

`lidar-shield` is read-only historical context. No code, results, dependencies,
milestones, or data paths are inherited from it. Detector and cooperative
perception frameworks are outside this initial project. S01 requires a separate
explicit invocation.

## Environment Setup

To create an isolated environment and install the hashed bootstrap lock on CPython 3.14:

```sh
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python --require-hashes -r requirements.lock
```

## Running Notebooks & Generating Outputs

Source notebooks in `notebooks/` are intentionally kept unexecuted in Git. They validate runner harness environment variables and provenance at runtime (`VP_REPO_ROOT`, `VP_RUN_DIR`, etc.), so they are executed via dedicated stage runner scripts in `scripts/`.

Each script runs tests, launches fresh Jupyter kernels, and seals an immutable evidence bundle under an ignored `artifacts/<run_id>/` directory containing fully executed `*.executed.ipynb` copies, alongside figures in `reports/figures/` and tables in `reports/tables/`.

### Commands by Notebook and Stage

| Target Notebook(s) in `notebooks/` | Stage | Command |
| :--- | :--- | :--- |
| `00_bootstrap.ipynb` | S00 Bootstrap | `.venv/bin/python scripts/execute_notebooks.py` |
| `01_synthetic_scenes.ipynb` | S01 Synthetic Scenes | `.venv/bin/python scripts/show_synthetic_scene.py` |
| `02_kinematics.ipynb`<br>`02_spatial_surplus.ipynb`<br>`02_availability.ipynb` | S02 Measurements | `.venv/bin/python scripts/measure_synthetic.py` |
| `03_clean_references.ipynb`<br>`03_score_and_ablations.ipynb` | S03 Fit & Score | `.venv/bin/python scripts/fit_and_score.py` |

### Run All Stages

To execute all notebooks across all stages in sequence:

```sh
.venv/bin/python scripts/execute_notebooks.py && \
.venv/bin/python scripts/show_synthetic_scene.py && \
.venv/bin/python scripts/measure_synthetic.py && \
.venv/bin/python scripts/fit_and_score.py
```

### Viewing Executed Notebooks and Outputs

1. **In IDE / JupyterLab**: Open the generated `artifacts/<run_id>/*.executed.ipynb` directly in VS Code or Jupyter (`.venv/bin/jupyter lab`).
2. **Export to HTML**: Convert the latest executed notebooks to HTML for instant viewing in any web browser:
   ```sh
   LATEST_RUN=$(ls -td artifacts/20* | head -n 1)
   .venv/bin/jupyter nbconvert --to html "$LATEST_RUN"/*.executed.ipynb
   ```

