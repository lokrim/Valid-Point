# S05 — Gated leave-one-sender-out consensus

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S04 has a recorded G3 disposition. Read `planning/04_consensus.md`; keep the K/S
baseline intact. Implement peer diagnostics first and only the preregistered
penalty-only ablation where prerequisites can be established.

## Exact deliverables

- `src/valid_point/consensus.py`, `configs/consensus.json`,
  `scripts/show_consensus_cases.py`, `tests/test_consensus.py`.
- `notebooks/05_consensus_cases.ipynb`;
  T05_consensus_eligibility/F05_peer_cases.

## Visible results and meaningful tests

Show tested-sender exclusion, raw counts, per-sensor clean normalization, peer
security groups, quorum>=2, timing/transform/view comparability, spread/conflict,
peer median and unknown reason. Two sensors on one RSU do not form two independent
peers. Use the frozen one-sided peer penalty and independently recalibrate the
max(K,S,P) ablation on clean calibration observations.

Display one attacker, two colluders, conflicting honest peers, missing peers,
changing membership, a uniquely useful honest viewpoint, correlated sensors/
shared occlusion and a Sybil identity case. Show that agreement need not mean
truth and a useful honest sender can disagree. Sweep added points for the tested
sender with peers fixed; then jointly change colluders to expose the assumption
boundary. Compare common eligible and all-attempt coverage.

Test strict leave-one-out construction, duplicate-group quorum rejection, peer
conflict=>unknown, invalid comparability=>unknown, deadline exclusion and
monotonic fixed-peer penalty. Test that failure to form consensus cannot quietly
yield perfect peer evidence.

## Stop/go

G4 unlocks only the eligible ablation demonstrated by evidence. If comparability
is not defensible, retain P=unknown/diagnostic, document the failure and permit
the K/S path to proceed independently. Never claim majority truth or Sybil defense.

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

