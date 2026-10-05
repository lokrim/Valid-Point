# S07 — Immutable deterministic attack overlays

Future implementation prompt. **Not executed during project setup.**

## Prerequisites and scope

S02/S04/S06 contracts, production reader and byte assumptions are available.
Read `planning/06_attack_simulation.md`. Implement synthetic overlays only in
this stage; real overlays remain behind S09 archive/time/label/transform gates.

## Exact deliverables

- `src/valid_point/attacks/__init__.py`, `attacks/overlays.py`,
  `attacks/manifests.py`; extend `io/pointcloud.py` only if required.
- `configs/attack_registry.json`, `scripts/build_overlay.py`.
- `tests/test_overlays.py`; extend `test_pointcloud_io.py`.
- `notebooks/07_overlay_roundtrip.ipynb`;
  T07_overlay_effects/F07_overlay_geometry.

## Visible results and meaningful tests

Implement seeded immutable point addition, count-preserving rearrangement,
removal, velocity spike/drift, jointly consistent odometry spoofing, dropout/
delay, on-off/trust-farming schedules, threshold-aware bounded search, colluding
peer schedules and benign faults. Include oracle-region and GT-free spatial
targets; no GT knowledge in attacks unless explicitly oracle-targeted.
Declare attacker knowledge/query budget and intended intensity.

Display originals and derived clouds/timelines and all intended, injected and
realized differences. Reload every derived cloud through the production reader,
checking field types/order, units/coordinates, finite values, counts, selected
IDs and hashes. Preserve failed/ineffective attempts and honest companions.
Show benign faults as benign, reader errors as invalid artifacts, not successful
detections.

Test unchanged original hashes, seed/order determinism, exact count effects,
count-preserving cases, timestamp boundaries, bad-field rejection, immutable
manifest lineage and production-reader round trip. Never resample until an
attack has the desired effect.

## Stop/go

G6 passes only with the full effect/attempt ledger and reader checks. Invalid
derived cases stay failed; real data remains untouched and full evaluation waits
for S08.

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

