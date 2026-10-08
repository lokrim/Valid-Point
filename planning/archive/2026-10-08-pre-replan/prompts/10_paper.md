# S10 — Paper figures, tables and limitations

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S08 complete evidence and an explicit S09 status exist. Read
`planning/07_validation.md`, `08_notebooks.md` and `09_decisions_and_gates.md`.
If real comparisons are incomplete, prepare a clearly scoped synthetic-only
report with incomplete real work visible. This stage must not tune methods or
run new attacks to improve the narrative.

## Exact deliverables

- `src/valid_point/reporting.py`, `scripts/export_paper.py`,
  `configs/paper_exports.json`, `tests/test_reporting.py`.
- `notebooks/10_paper_results.ipynb`.
- T10_claim_evidence, T10_protocol and F10_overview, plus publication-format exports
  of all available named figures/tables listed in `07_validation.md`.
- `reports/results.md`, `reports/limitations.md`, and an ignored immutable
  reproducibility bundle under the run, with a file/checksum index.

## Visible results and meaningful tests

Recreate report figures/tables from frozen measurement artifacts, showing inputs,
track, source/seed provenance and missing outputs. Include per-segment results,
wide grouped uncertainty, clean reference/false-alarm distributions, count-trust
curves, consensus failures, oracle gap, threshold/ablation comparisons, byte
timelines and bandwidth-quality proxy curves where actually run. Include a
negative/failed-case table, all-attempt coverage and honest-view loss.

Map each proposed claim to executed notebook section, named table/figure, run,
denominator, assumption and limitation. State that conformity is not a
probability, oracle results do not imply GT-free readiness, and proxy utility
is not AP. AP@0.5/0.7, detector-based utility, ROBOSAC/MADE comparisons, cross-
dataset transfer, temporal recovery and probability reliability/ECE stay “not
run” unless their independently gated evidence exists.

Test export provenance and input hashes, table-value reconciliation with frozen
metrics, undefined-cell preservation and claim-link existence. Inspect every
rendered figure for readable units, counts, legends and uncertainty. Do not
claim a notebook ran if only cached outputs were copied.

## Stop/go

G10 passes when every supported claim is traceable and every unsupported claim
removed or explicitly deferred. A negative-result paper is acceptable. Stop for
review; do not publish, submit, install a detector or run a new stage automatically.

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

