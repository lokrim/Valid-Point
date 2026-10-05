# S03 — Clean references, score combination and ablations

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S02 raw measurements are verified; reference/calibration/test seeds are disjoint.
Read `planning/03_phase1_evidence.md` and `07_validation.md`. Implement the
proposed clean reference hierarchy and T=1-max(K,S), static-sensor S-only rule,
strict unknown intervals, separate clean operating calibration and diagnostics.

## Exact deliverables

- `src/valid_point/references.py`, `scoring.py`, `calibration.py`, `ablations.py`.
- `configs/reference_protocol.json`, `scripts/fit_and_score.py`.
- `tests/test_references.py`, `test_scoring.py`, `test_calibration.py`.
- `notebooks/03_clean_references.ipynb`, `03_score_and_ablations.ipynb`.
- T03_reference_support, T03_ablations, F03_clean_distributions,
  F03_threshold_ablation and F03_trust_point_count.

## Visible results and meaningful tests

Display raw clean reference distributions, u/b, bin support, broader fallback
and zero-scale/unsupported contexts. Engineering validity, fitted ranges,
calibration threshold and future policy parameters must be visibly distinct.
Show all hand cases in the score contract and a literal injected-point-count
sweep on fixed regions, labeled illustrative fixtures rather than a full attack
study. Plot the identity of the strongest anomaly and strict unknown coverage.
Compare K-only, S-only and max scores on common support and all decisions.

Use only clean reference observations for ranges; calibrate alpha=1% on separate
clean data with frozen ties/order-statistic rule. Show achieved FPR, support and
uncertainty; a no-power threshold is a negative result. Test split lineage,
training-only fitting, degenerate fallback, max behavior, missing factors,
bounded outputs and nonincreasing T under point addition. Never hand-fix factor
weights, tune on held-out attacks or treat T as a probability.

## Stop/go

G2 requires reproducible semantics, leakage prevention and visible calibration
limits, not high AUROC. Learned/adaptive weights require a later gate; stop here.

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

