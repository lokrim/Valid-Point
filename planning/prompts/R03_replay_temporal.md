# R03 — real-cloud overlays and temporal demonstration

## Prerequisites and scope

GR2 causal/reader/boundary checks pass with explicit component dispositions and a development factor freeze. Use mini_7 only. Read planning/06_attack_simulation.md, temporal_spec.md and 07_validation.md. Implement the five primary overlay families plus zero controls, EWMA and matched clean/attacked replay; execute only one middle-severity sustained case per family and one displacement burst case for a bounded development demonstration. Keep all companions.

## Exact deliverables

Create `src/valid_point/attacks/overlays.py`, `attacks/manifests.py`, `temporal.py`, adapt replay and score records, add `configs/development_replay.json`, `scripts/replay_development.py`, `tests/test_overlays.py`, `tests/test_temporal.py`, `tests/test_replay_isolation.py`, and `notebooks/R03_replay_temporal.ipynb`. Add strict production PCD writer/reloader support; synthetic JSON is not a substitute. Keep intended/injected/realized and failed injection/rejection ledgers.

For demonstration normalization only, fit actual raw clean factors from the first 10 s of mini_7 using explicitly named exploratory support (>=50 rows, one segment); never invent multiple scene IDs to pass the final two-segment rule. Fit diagnostic thresholds, if support permits the unchanged >=200 known rule, from subsequent clean observations only, otherwise alarms remain unavailable. Mark all mini_7 score plots development-only; neither reuse of its scene nor internal time blocks establish independent calibration. Final fitting/support rules remain unchanged for R05. If exploratory scale degenerates, show raw timelines and unknown scores rather than fabricate normalization.

Implement the exact elapsed-time EWMA, warm-up, missing hold/reset, state isolation and reference-version reset. Derive tau choice only from clean temporal coverage per specification. Attacked geometric history comes from the attacked arm; no clean shadow. No attack schedule input to scorer/state. Reference ranges stay frozen. Use actual time axes with evaluator-only interval annotations after decision sealing.

## Meaningful tests and visible evidence

Test row-count effects, per-cell count preservation, deterministic traversal-independent selection, unchanged base/companion hashes, identity write/read tolerances and malformed reader rejection. Validate every executed derived cloud through the clean production reader. Test analytic irregular-time recurrence, initialization, short/long gaps, duplicate/reversed time, checkpoint resume, warm-up, no cross-agent/arm state and prefix invariance. Repeat actual changed/withheld evaluator boundary tests for scores and complete temporal state, including a deliberate leakage control.

Show clean/attacked geometry, raw/normalized factors, memoryless and temporal conformity, null alarms where uncalibrated, honest-companion traces and history contamination. Include one benign noise and calibration/timing-uncertainty control; define/freeze remaining benign grid before R04. Export T_R03_attempts, T_R03_roundtrip, T_R03_state_checks, F_R03_geometry and F_R03_timelines. No monotonic attack decline or guaranteed recovery assertion.

## Failure behavior and stopping point

Reader rejection/zero realized effects remain attempts; no resampling for success. Broken causality, state or original immutability blocks GR3; absent empirical calibration or no detectable effect is documented, not repaired by labels. Stop after the development demonstration; no C0–C3 or H content/outcomes.

## Required working and evidence rules

Work only in Valid Point, package `valid_point`; do not read/copy sibling code, data or results. Read the current planning index, source/method contracts, audit and history first. Execute only this R stage. Keep historical artifacts/source notebooks unchanged; use small importable Python functions, thin scripts and new R notebooks. No detector framework, external publication or later-stage auto-run.

Operational scorer and temporal state must never receive labels, GT boxes, attack flags/schedules/masks, clean counterparts or evaluator outcomes. Use causal inputs with declared availability and strict unknowns; no honesty probability, forced attack curve or favorable-result acceptance test. Freeze predictions before evaluator joins. Preserve failed attempts and every honest companion.

Execute listed notebooks top-to-bottom in fresh kernels, show units/input geometry/raw records/unknowns/failures and actual plots. Save a new immutable run with exact config, seeds, source/environment/input/output hashes, split/reference/calibration lineage, logs, meaningful test results, executed notebooks and gate. Export named figures PDF/SVG+PNG and full tables CSV+Markdown with provenance, following planning/08_notebooks.md. Keep technical correctness separate from scientific outcomes. Append dated findings/changed assumptions to planning/history.md and update planning/progressplan.md and planning/checklist.md with actual evidence links. Stop at this stage's gate and report limitations; do not invoke the next prompt.
