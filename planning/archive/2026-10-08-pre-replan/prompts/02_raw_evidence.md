# S02 — Phase 1 raw evidence

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S01 contracts/reader/scenes passed G1. Read `planning/03_phase1_evidence.md`.
Implement raw measurements and explicit eligibility only; fitting and scoring
belong to S03. Use hand-defined small cases, not an attack generation framework.

## Exact deliverables

- `src/valid_point/evidence/__init__.py`, `evidence/kinematics.py`,
  `evidence/spatial.py`, `evidence/availability.py`.
- `configs/raw_evidence.json`; `scripts/measure_synthetic.py`.
- `tests/test_kinematics.py`, `test_spatial.py`, `test_availability.py`.
- `notebooks/02_kinematics.ipynb`, `02_spatial_surplus.ipynb`,
  `02_availability.ipynb`.
- T02_kinematic_raw/F02_motion, T02_region_counts/F02_regions,
  T02_eligibility/F02_deadlines.

## Visible results and meaningful tests

Kinematics shows displacement minus causally predicted displacement in metres,
actual dt, frames and velocity units; compare legitimate acceleration, inconsistent
reports and jointly consistent spoofed reports as hand fixtures. Explain why
self-consistency lacks independent motion evidence. Spatial shows counts in
externally fixed regions, including zero, dense legitimate returns, changed
content, unsupported transforms and unknown visibility. No symmetric “closer
count is more trustworthy” reward and no group point-share factor. Availability
shows freshness/health/transform status independently of intent.

Test hand-computable residuals/counts, boundary points and units, causal sample
selection, invalid dt, missing velocity never mapped to zero penalty, absent
cloud versus empty, malformed fields, and count monotonicity under literal
added-point fixtures. Region/source provenance must be visible in each notebook.

## Stop/go

Proceed to fitting only if the raw contracts and unknown states pass. Record
consistent-spoof/removal limitations now. Do not emit an uncalibrated trust
probability or temporal alarm.

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

