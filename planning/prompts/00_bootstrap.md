# S00 — Bootstrap and notebook conventions

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

The researcher has reviewed the planning-only scaffold and invoked this prompt.
Read `planning/08_notebooks.md`, `09_decisions_and_gates.md` and all three ongoing
records. Establish the smallest reproducible scientific environment and notebook
execution/export conventions. Do not build scenes, factors, overlays or policies.
Choose only necessary Python-native packages, record why, and create a lock with
resolved versions if dependencies are now authorized. No detector framework.

## Exact deliverables

- Update `pyproject.toml`; create `requirements.lock` with environment/version
  provenance and `configs/bootstrap.json`.
- Create `src/valid_point/provenance.py` and thin
  `scripts/execute_notebooks.py`; stage-specific computation comes later.
- Create `tests/test_bootstrap.py` and `notebooks/00_bootstrap.ipynb`.
- Export T00_environment, T00_scaffold and F00_structure.

## Visible results and meaningful tests

Show interpreter/package origin, dependency versions, file tree, configuration,
source hash and output naming. Explicitly label research measurements and results
“not run”; never fabricate a scientific smoke result. Demonstrate a tiny
non-scientific export round trip and missing-provenance failure. Test manifest
required fields, stable hashes for identical bytes, invalid config rejection and
fresh-kernel execution from the repository without previous state. Ensure no
research-stage execution or download is triggered by importing the package.

## Stop/go

G1 infrastructure portion passes only with an independently rerunnable notebook,
provenance and test evidence. Otherwise record the blocker. Scientific work waits
for explicit invocation of S01.

## Boundaries and working rules

Work only on this invoked stage in Valid Point (`valid-point`, package
`valid_point`). Read the current planning documents and records before changing
anything. `lidar-shield` is read-only context, never code/data/results to copy or
a dependency. Do not execute another stage prompt. Use small importable Python
functions; notebook cells call, explain and display them. Do not introduce a
detector/cooperative-perception framework. A failed hypothesis is a valid result;
never invent favorable results or hide failed attempts.

The decision unit is sender/frame/deadline; no future information. Keep raw
measurements, normalized evidence, conformity score, alarm/state and next-frame
allocation separate. T is not an honesty probability. Use strict unknown states,
no manually fixed factor weights, no point-share corroboration, and no
zero-return accusation under unknown visibility. Keep oracle-box and GT-free
namespaces separate; evaluator GT may never enter GT-free score or policy.
No unrequested download or later-gated experiment is authorized by this prompt.

## Required evidence and record updates

Execute every listed notebook from a fresh kernel, top to bottom. Display input
geometry/data (or environment inventory for bootstrap), units, deadlines, config,
seeds, raw measurements, unknown/not-applicable states, outputs, failures and an
evidence-based conclusion. Provide named tables/figures below and a visible
pass/fail/blocked gate; code or unexecuted notebooks alone cannot pass. Keep
scientific computation in the listed importable modules. Run the meaningful
tests specified below, not implementation-mirroring snapshots.

Save an immutable `artifacts/<run_id>/` manifest, exact configuration and seeds,
source/revision/input hashes, code/environment versions, split/track and
reference/calibration lineage, execution log, test results, output hashes,
executed notebooks and `gate.md`. Export named figures as PDF/SVG plus PNG and
tables as CSV plus a readable format under `reports/figures/` and
`reports/tables/`, with run/provenance sidecars and stage/track/segment suffixes.
Do not overwrite earlier runs. Generated artifacts/data stay Git-ignored; source
notebooks, modules and frozen configs are versioned. Provide reviewer-accessible
evidence links without publishing externally unless authorized.

Append dated decisions, changed assumptions and reasons to
`planning/history.md`; update stage status/dependencies/risks in
`planning/progressplan.md`; update specific acceptance rows and actual evidence
links in `planning/checklist.md`. Record failures, negative results and blocked
claims in all relevant records. Stop after this stage and present its evidence
for review; do not auto-launch the next prompt.

