# Valid Point

Valid Point studies whether explainable, ground-truth-free sender conformity
checks can detect specified corruptions in cooperative LiDAR observations and
help allocate bandwidth without unnecessarily excluding honest viewpoints.
The repository is `valid-point`; the Python package is `valid_point`.

**Status: setup and planning only.** There are no research algorithms, datasets,
executed notebooks, attacks, simulations, or scientific results here. No
dependencies have been installed. The package has no runtime dependencies and
can be imported from `src/`; implementation begins only after plan review.

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
| `src/valid_point/`, `tests/`, `scripts/` | Future importable computation, meaningful checks, small entry points |
| `notebooks/`, `configs/` | Future visible stage evidence and frozen configurations |
| `planning/` | Method contracts, decisions, provenance, acceptance, staged prompts |
| `data/`, `artifacts/` | Ignored raw inputs and reproducible generated runs |
| `reports/figures/`, `reports/tables/` | Ignored report-ready exports with provenance |

`lidar-shield` is read-only historical context. No code, results, dependencies,
milestones, or data paths are inherited from it. Detector and cooperative
perception frameworks are outside this initial project. Stop at planning until
the researcher reviews the proposed gates.
