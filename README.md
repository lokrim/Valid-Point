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

To rerun S00 on CPython 3.14, create an isolated environment, install the
hashed bootstrap lock, then run the thin entry point from the repository root:

```sh
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python --require-hashes -r requirements.lock
.venv/bin/python scripts/execute_notebooks.py
```

The runner sets the source path for both tests and a new Jupyter kernel. It
creates a new ignored `artifacts/<run_id>/` bundle and uniquely named exports
under `reports/`. The [checklist](planning/checklist.md) links the executed
S00 evidence. The source notebook is intentionally unexecuted in Git.
