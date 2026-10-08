> **SUPERSEDED 2026-10-08 — historical S-stage prompt; do not execute as the current plan.**
> See [current R-stage index](README.md), [audit corrections](../evidence_audit.md) and H011 in [history](../history.md). The original body below is preserved for provenance.

# S09 — Four-or-more-segment intake and grouped evaluation

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S08 evidence exists; researcher has resolved acquisition/storage resources.
Read `planning/sources.md`, `02_data_protocol.md`, `03_phase1_evidence.md`,
`05_bandwidth.md`, `07_validation.md`. This stage has an intake gate before
overlays and an outer-freeze gate before results. Never auto-download the release.

## Exact deliverables

- `src/valid_point/io/mixed_signals.py`, `dataset.py`,
  `evaluation/splits.py`, `evaluation/real.py`.
- `configs/segment_roles.json`, `configs/real_evaluation.json`;
  `scripts/intake_segment.py`, `scripts/evaluate_real.py`.
- `tests/test_mixed_signals.py`, `test_splits.py`; extend GT-isolation/reader tests.
- `notebooks/09_real_intake.ipynb`, `09_segment_timelines.ipynb`,
  `09_grouped_evaluation.ipynb`.
- T09_inventory/F09_geometry, T09_clean_strata, T09_attack_metrics,
  T09_ablations, T09_oracle_gap, T09_policies, T09_failures;
  F09_segment_timelines/F09_bandwidth_quality.

## Intake and frozen evaluation

Recheck official metadata at a pinned revision, public labels and resource budget.
mini_7 and mini_10 are segment TARs containing frames; do not offer individual
PCD downloads. Acquire only explicitly authorized archives, one at a time; do
not assume any is locally present. Proposed roles: mini_7 development only,
mini_10/11/12/13 comparisons C0–C3 and mini_14 untouched final H. Freeze roles
from availability/metadata before outcomes; no outcome-based replacements.

Validate archive hashes/safe members, timestamp units/association, label presence
versus empty labels and authoritative coordinate transforms on a bounded sequence
before real overlays. If labels/timing/geometry fail, report the blocked segment.
Fewer than FOUR distinct labeled comparison segments beyond development means
the real study is incomplete. Keep every agent/frame/clean/attack variant in its
segment. Outer fold k tests Ck, calibrates clean C(k+1 mod 4), and fits clean
references only on the other two. All methods and grids freeze before any outer
outcome is revealed; no global fitted caches. Real policy uses GT-free scores,
actual bytes and causal observations. Final H is opened only after a documented
final freeze, using C0–C2 fitting and C3 clean calibration.

## Visible results and meaningful tests

Execute timelines fresh for every comparison segment/track; show clean and
attacked measurements, unknowns, failed attacks, thresholds and quotas. Report
all segments plus macro aggregate, paired grouped intervals, coverage,
oracle gap, benign faults and honest-view loss. Four groups imply wide uncertainty.
Show ideal-arrival assumptions explicitly, not purported measured network delay.
Test parser/transform/time hand fixtures, missing labels, archive safety, split
disjointness, clean-only fitting lineage and GT-free score/quota isolation.

## Stop/go

G8 requires validated intake and >=4 labeled comparisons; G9 requires frozen
per-segment evidence. Retain incomplete/negative outcomes and block unsupported
real policy claims. Do not proceed automatically to paper generation.

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

