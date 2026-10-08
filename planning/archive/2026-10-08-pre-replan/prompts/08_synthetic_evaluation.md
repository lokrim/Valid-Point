# S08 — Synthetic attack and policy evaluation

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S03–S07 technical gates are resolved and consensus/GT-free limitations recorded.
Read `planning/06_attack_simulation.md`, `07_validation.md` and
`05_bandwidth.md`. Freeze scenario/seed/metric/threshold/budget grids before
opening held-out synthetic seeds. No real data acquisition.

## Exact deliverables

- `src/valid_point/simulation.py`, `evaluation/metrics.py`,
  `evaluation/runner.py`, `evaluation/statistics.py`.
- `configs/synthetic_evaluation.json`, `scripts/evaluate_synthetic.py`.
- `tests/test_metrics.py`, `tests/test_evaluation.py`.
- `notebooks/08_synthetic_evaluation.ipynb`.
- T08_attack_metrics, T08_benign_false_alarms, T08_coverage, T08_tradeoffs,
  T08_policy_bound; F08_attack_curves, F08_benign_stress, F08_sweeps,
  F08_bandwidth_quality, F08_proxy_utility.

## Visible results and meaningful tests

Run every predeclared attack/benign family, intensity, compromised fraction,
collusion and adaptive case, retaining all attempts and honest companions.
Show per-family AUROC/AUPRC on known scores, all-attempt and scored recall,
achieved frozen-threshold benign FPR, abstention and precision at 1/10/50%
stated prevalence. Show reference/threshold sensitivity and K/S/P/oracle/GT-free
ablations with common-support and full-denominator results. Use paired
independent-seed uncertainty, not frame pseudoreplication.

Plot equal actual-byte quality/corruption/honest-view curves and causal timelines,
including reserve abuse, harmful packing and audit cost. Compute leave-one-agent-
out PROXY utility; a hindsight POLICY bound must be exact or mathematically
bounded in a small finite case, otherwise label it only a comparator.
Memoryless threshold crossings are not temporal controller detection/recovery.

Test metrics on hand examples including undefined/one-class/all-unknown inputs,
scenario completeness, causal censored-observation replay, exact-byte matching,
group-preserving resampling and evaluator isolation.

## Stop/go

G7 requires complete reproducible evaluation and negative results, not favorable
performance. No temporal controller, probability ECE or detector AP claims are
permitted without their separate gates. Stop before real intake.

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

