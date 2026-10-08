# R06 — untouched final check

## Prerequisites and scope

R05 disposition and a sealed method/protocol for H; explicit mini_14 acquisition/resource authorization; exposure ledger confirms only public metadata has been inspected. Read planning/02_data_protocol.md and 07_validation.md. If comparison outcomes prompted a method change, record a new study and pre-H freeze first; never claim that version was independently validated on C0–C3. Run only mini_14 final replay.

## Exact deliverables

Reuse the production intake/replay/evaluator with `configs/final_holdout.json`, `scripts/evaluate_final.py`, and `notebooks/R06_final_holdout.ipynb`. Refit frozen method references from clean C0–C2 and calibrate independently on clean C3, using actual pipelines and the same reset/support rules. Verify pinned mini_14 archive size/hash/safety and all metadata assumptions. Record first content/outcome access time and method hash before any inspection. Generate the full frozen intervention/benign/ablation grid and companions; seal predictions before evaluation. Export T_R06_exposure, T_R06_metrics and F_R06_timelines plus complete geometry/coverage/failures as applicable.

## Meaningful tests and visible evidence

Check H never enters fitting/calibration/config selection, all variants stay with H, output hashes and attempt denominators reconcile, production-reader integrity and evaluator isolation still hold. Show H separately from comparison macro results, with real seconds/metres, unknowns, no-power thresholds and censored timing metrics. A single final segment receives no between-scene confidence interval.

## Failure behavior and stopping point

Once exposed, H remains exposed even if a run fails. Technical repairs require a recorded amendment and rerun disclosure, never a new “untouched” claim. Missing authorization/access or invalid schema is blocked final evaluation; retain that disposition. Stop at GR6 before paper tuning or publication.

## Required working and evidence rules

Work only in Valid Point, package `valid_point`; do not read/copy sibling code, data or results. Read the current planning index, source/method contracts, audit and history first. Execute only this R stage. Keep historical artifacts/source notebooks unchanged; use small importable Python functions, thin scripts and new R notebooks. No detector framework, external publication or later-stage auto-run.

Operational scorer and temporal state must never receive labels, GT boxes, attack flags/schedules/masks, clean counterparts or evaluator outcomes. Use causal inputs with declared availability and strict unknowns; no honesty probability, forced attack curve or favorable-result acceptance test. Freeze predictions before evaluator joins. Preserve failed attempts and every honest companion.

Execute listed notebooks top-to-bottom in fresh kernels, show units/input geometry/raw records/unknowns/failures and actual plots. Save a new immutable run with exact config, seeds, source/environment/input/output hashes, split/reference/calibration lineage, logs, meaningful test results, executed notebooks and gate. Export named figures PDF/SVG+PNG and full tables CSV+Markdown with provenance, following planning/08_notebooks.md. Keep technical correctness separate from scientific outcomes. Append dated findings/changed assumptions to planning/history.md and update planning/progressplan.md and planning/checklist.md with actual evidence links. Stop at this stage's gate and report limitations; do not invoke the next prompt.
