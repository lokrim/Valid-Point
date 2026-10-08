# R04 — freeze the comparison experiment

## Prerequisites and scope

GR3 complete or scientifically limited with technical integrity. Read all canonical method/replay/evaluation/split documents. Resolve any necessary implementation bug on development only with a new GR3 run. Prepare the final protocol without loading comparison/final cloud or label bodies and without computing their outcomes. Public archive metadata remains allowed.

## Exact deliverables

Create `configs/segment_roles.json`, `configs/replay_evaluation.json`, `src/valid_point/evaluation/splits.py`, `evaluation/metrics.py`, `tests/test_splits.py`, `tests/test_metrics.py`, `scripts/freeze_protocol.py`, and `notebooks/R04_protocol_freeze.ipynb`. Save a content-addressed freeze manifest and exposure ledger covering source/config versions, selected factor arms and sensor roles, transforms/clock bounds, cell/voxel/crop/support/fallback settings, tau/gap/warm-up, split table, actual-path reference fitting and separate calibration, attack/severity/schedule/benign grid, seed derivation, attempted-event/episode metrics and undefined handling, runtime/storage limits, and report selection rules.

Keep mini_7 development; C0–C3=mini_10–13, H=mini_14. Metadata-only replacements need dated reasons; no outcome-driven substitutions. Set final H fit=C0–C2, calibration=C3. Freeze all folds/ablations together and require prediction sealing before outcomes. No global fit cache or algebraically constructed calibration anomalies. Record comparison/final download authorization and the actual retention budget; absent authorization is a resource block on R05/R06, not a reason to acquire now.

## Meaningful tests and visible evidence

Test segment/variant leakage rejection, references disjoint from calibration/test, sensor-specific threshold lineage, warm-up eligibility and no-power/insufficient-support thresholds. Hand-check all-attempt/eligible/realized denominators, failed injections, empty classes, missing scores, preexisting alarm, censored delay and undefined recovery. Verify grouped resampling preserves pairing and does not count frames as independent. Use small arithmetic fixtures explicitly labeled as tests, never as empirical calibration. T_R04_splits, T_R04_parameters and T_R04_lineage must let a reviewer reconstruct exactly what R05 will run.

## Failure behavior and stopping point

Ambiguous method/metric defaults or leakage errors block GR4. Resolve from mini_7 or explicit assumptions, never comparison outcomes. Stop at sealed protocol and resource disposition; do not launch acquisition or evaluation automatically. An unsupported factor/no-power expectation is not a failed technical gate.

## Required working and evidence rules

Work only in Valid Point, package `valid_point`; do not read/copy sibling code, data or results. Read the current planning index, source/method contracts, audit and history first. Execute only this R stage. Keep historical artifacts/source notebooks unchanged; use small importable Python functions, thin scripts and new R notebooks. No detector framework, external publication or later-stage auto-run.

Operational scorer and temporal state must never receive labels, GT boxes, attack flags/schedules/masks, clean counterparts or evaluator outcomes. Use causal inputs with declared availability and strict unknowns; no honesty probability, forced attack curve or favorable-result acceptance test. Freeze predictions before evaluator joins. Preserve failed attempts and every honest companion.

Execute listed notebooks top-to-bottom in fresh kernels, show units/input geometry/raw records/unknowns/failures and actual plots. Save a new immutable run with exact config, seeds, source/environment/input/output hashes, split/reference/calibration lineage, logs, meaningful test results, executed notebooks and gate. Export named figures PDF/SVG+PNG and full tables CSV+Markdown with provenance, following planning/08_notebooks.md. Keep technical correctness separate from scientific outcomes. Append dated findings/changed assumptions to planning/history.md and update planning/progressplan.md and planning/checklist.md with actual evidence links. Stop at this stage's gate and report limitations; do not invoke the next prompt.
