> **SUPERSEDED 2026-10-08 — historical S-stage prompt; do not execute as the current plan.**
> See [current R-stage index](README.md), [audit corrections](../evidence_audit.md) and H011 in [history](../history.md). The original body below is preserved for provenance.

# S06 — Byte accounting and next-frame quota policies

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S04 has an explicit viability disposition, and S05 status (passed or unavailable)
is recorded. Read `planning/05_bandwidth.md`. Implement small hand-sized policy
cases and a labeled task proxy, not a full attack sweep. Operational claims
remain blocked if GT-free viability failed.

## Exact deliverables

- `src/valid_point/serialization.py`, `bandwidth.py`, `payloads.py`, `proxy.py`.
- `configs/bandwidth.json`, `scripts/show_byte_policy.py`.
- `tests/test_serialization.py`, `test_bandwidth.py`, `test_proxy.py`; extend
  `test_gt_isolation.py` to quotas.
- `notebooks/06_next_frame_bytes.ipynb`; T06_byte_ledger/F06_byte_timeline.

## Visible results and meaningful tests

Actually serialize payloads; validate the proposed header and point record costs.
Show attempted/transmitted/admitted/processed/fused bytes, control/audit costs,
insufficient header budgets and demand caps. T_f governs f+1 only; quota decisions
use available observations, expire stale scores and handle cold-start unknowns.
Reduced payload counts must not be interpreted as full-cloud counts: show
censored evidence, unknown fallback, counted audit rounds and feedback starvation.

Compare uniform, calibrated hard gate, linear proportional, smooth continuous
and explicit unknown reserve/ablations. Separate common cap from equal actual
bytes; show unspent budget and matched feasible runs. Include the absolute
T-times-uniform-quota ablation. Compare seeded honest point selection with
malicious harmful packing as literal fixtures. Show task coverage, contamination
and honest unique-view loss separately, not AP.

Test byte conservation, integer allocation, deterministic ties, zero/all-unknown/
all-gated weights, no GT policy input, no retroactive savings, no hidden full
cloud after truncation, and proxy hand cases. State trusted enforcement location.

## Stop/go

G5 requires exact ledgers and causal decisions. Receiver dropping alone cannot
pass a network-saving claim. Freeze proposed policy parameters only after
synthetic development evidence; stop before attack implementation.

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

