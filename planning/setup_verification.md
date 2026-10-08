# Setup verification — 2026-10-05

This is a structural/documentary audit, **not a scientific result**. Executed
with the existing system Python 3.14.4, standard library and installed Git. No
dependency installation, package build, dataset download, notebook execution,
attack generation or simulation was performed. Package metadata declares Python
>=3.11; other interpreters/build isolation have not been tested.

| Check | Observed evidence |
| --- | --- |
| Required directory scaffold | All 10 required directory paths exist, including nested figures/tables and prompts. |
| Empty package import | Imported `valid_point` from this project's `src/valid_point/__init__.py` with bytecode disabled. AST contains one docstring statement only. |
| Scientific implementation absence | Only one Python source file exists: package `__init__.py`; zero `.ipynb` notebooks. |
| Raw/generated input absence | `data/` and `artifacts/` contain only their README instructions; report folders contain only instructions. |
| Packaging syntax | `tomllib` parsed `pyproject.toml`; project name `valid-point`, runtime dependencies `[]`. No detector/cooperative framework dependency. |
| Future prompts | Exactly 11 numbered prompts. Each has prerequisites, exact deliverables, notebook/test paths, fresh-kernel evidence, provenance, stop/go, and all three record update requirements. |
| Git ignores | Tested 17 representative paths with `git check-ignore --no-index` in a disposable temporary Git directory. Raw archives/clouds, nested artifacts, generated reports/figures/tables, environment and bytecode ignored; README placeholders, source, notebooks, configs and plans retained. |
| Local documentation links | Resolved local Markdown file destinations; verified no broken file links after this audit file was added. |
| User requirement coverage | [Requirement matrix](requirements_coverage.md) maps every requested category to a method document/prompt and acceptance item. This is specification coverage only. |
| Source packaging | [Source record](sources.md) cites release card, exact revision and public archive inventory. No archive contents were validated. |
| Research status | All scientific checklist rows pending; only setup/documentation rows verified. G0 awaits researcher review. |

The temporary ignore-check directory was automatically removed. No Git repository
was initialized in this project during the check. No archive is assumed locally
present. Historical `lidar-shield` documents were read only and no sibling file
was changed. The plan's sample scores are hand calculations, not measurements.

Review starts at [planning index](README.md), then
[decisions and gates](09_decisions_and_gates.md). The next action is review;
implementation prompts remain unexecuted.

## 2026-10-08 planning revision verification

The setup-only statements above describe 2026-10-05 and must not be read as today's package status. S00–S04 now exist at the limited scope in [evidence audit](evidence_audit.md). This revision preserved pre-edit planning bytes, read and hashed existing artifacts, verified public source revisions and remodeled the canonical documents/prompts. No scientific tests/notebooks/stages or large downloads were executed during revision. Current document/link/preservation checks are recorded in `audit/2026-10-08-planning-checks.json` after editing; they establish planning coherence, not dataset feasibility or detection performance.
