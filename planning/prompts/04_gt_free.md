# S04 — GT-free spatial evidence and oracle gap

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S03 passed technical G2 and has frozen synthetic reference/calibration bundles.
Read `planning/03_phase1_evidence.md` and GT-free claim gates in
`09_decisions_and_gates.md`. Establish the required operational-input path;
oracle evidence remains only a separately named research track.

## Exact deliverables

- `src/valid_point/regions.py`, `gt_free.py`, `oracle.py`,
  `evaluation/__init__.py`, `evaluation/gap.py`.
- `configs/spatial_tracks.json`; `scripts/compare_spatial_tracks.py`.
- `tests/test_regions.py`, `tests/test_gt_isolation.py`.
- `notebooks/04_gt_free_oracle_gap.ipynb`; T04_gap_cases/F04_oracle_gap.

## Visible results and meaningful tests

Use receiver-owned fixed tiles including empty regions, frozen before reading
the tested cloud. Range/context cannot be improved by sender-controlled inputs;
use a documented broader context or unknown. Compare to oracle boxes at paired
decisions, with independently fitted references/calibration per track. An optional
ego-only geometric proposal ablation must be small and can remain deferred if it
would obscure the first result.

Show missed objects, empty regions, extra/merged/split proposals, unique honest
views, changing content, association ambiguity, outside-ROI additions, false
alarms and abstentions. Report the oracle-minus-GT-free gap on common support and
all attempts. GT can measure outcomes and object-count strata only. Test that
withholding/permuting evaluator labels leaves GT-free scores identical, changing
sender points cannot alter region definitions, and added suspicious points
cannot improve T at fixed eligible context. Include the count-preserving blind spot.

## Stop/go

G3 records whether the GT-free score is defensible under stated assumptions.
A failure is an explicit negative result and blocks operational readiness/real
policy claims. Do not import a detector to conceal the failure. Stop for review.

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

