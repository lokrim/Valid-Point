> **SUPERSEDED 2026-10-08 — historical S-stage prompt; do not execute as the current plan.**
> See [current R-stage index](README.md), [audit corrections](../evidence_audit.md) and H011 in [history](../history.md). The original body below is preserved for provenance.

# S01 — Synthetic scene contracts and first visualization

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S00 evidence exists and conventions work. Read `01_research_contract.md`,
`02_data_protocol.md`, `03_phase1_evidence.md` and `08_notebooks.md` in planning.
Implement tiny synthetic scenes with ordinary Python/NumPy geometry only, with
evaluator truth kept separate. Do not implement scores, attacks or quota policies.

## Exact deliverables

- `src/valid_point/contracts.py`, `synthetic.py`, `io/__init__.py`,
  `io/pointcloud.py`: causal record contracts and one small canonical synthetic
  point-cloud format/production reader used by later overlays.
- `configs/synthetic.json`, `scripts/show_synthetic_scene.py`.
- `tests/test_contracts.py`, `tests/test_synthetic.py`,
  `tests/test_pointcloud_io.py`; `notebooks/01_synthetic_scenes.ipynb`.
- T01_scene_contract, T01_unknown_states and F01_scene_views.

## Visible results and meaningful tests

Show a road plane, static geometry, moving object and multiple viewpoints with
occlusion and one uniquely useful honest view. Display native/receiver axes,
transforms, source/arrival/deadline times, and a point table. Include nonempty,
present empty, absent, late, malformed and unavailable-kinematics cases. Unknown
visibility must remain unknown. Declare independent sensor/security groups.
Partition generator seeds by complete scene (development 0–9, reference 100–109,
calibration 200–209, test 300–329 as proposed, amended before use if needed).
Test deterministic generation independent of traversal order, coordinate inverse
round trips, reader field/count preservation, exact-time causality, duplicate keys,
and disjoint seed families. Show the counterexample for empty versus absent.

## Stop/go

G1 passes when geometry and contracts are visibly auditable and reproducible.
Do not pass a future GT-free or score claim merely because scene truth exists.

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

