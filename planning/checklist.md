# Evidence checklist — revision 2026-10-08

Old checklist bytes are preserved in [the snapshot](archive/2026-10-08-pre-replan/checklist.md). Historical G01 “GT isolation verified” is retracted at that scope; see [audit](evidence_audit.md). R-stage IDs below are not the old checklist's R01/R02 reference-fit rows.

| ID | Required proof | Current state |
| --- | --- | --- |
| PLAN | Coherent authorized replan, append-only correction, superseded prompts and preserved prior bytes | Complete documentary work; [history](history.md), [snapshot manifest](archive/2026-10-08-pre-replan/snapshot_manifest.json) |
| AUDIT | Computation vs fixtures vs empirical validation; input/calibration/boundary/gate scrutiny | Complete; [audit](evidence_audit.md), [22-bundle hash check](audit/2026-10-08-artifact-verification.json) |
| SOURCE | Primary sources pinned, source hashes, exact public archive metadata, unavailable fields | Complete documentation-only; [sources](sources.md), [matrix](dataset_field_matrix.md) |
| DATA | Authorized mini_7 hash, safe inventory, real headers/columns, time/transform checks, geometry | **Complete for R01 intake:** [GR1](../artifacts/20261008T192922Z-R01/gate.md), [executed notebook](../notebooks/R01_development_intake.ipynb), [schema](../artifacts/20261008T192922Z-R01/T_R01_schema.json), [timing](../artifacts/20261008T192922Z-R01/T_R01_timing.json), [figure](../artifacts/20261008T192922Z-R01/F_R01_geometry.png), [84-test report](../artifacts/20261008T192922Z-R01/test_results.xml). Temporal/cross-agent/K limits remain conditional. |
| FACTOR | Raw causal D/G feasible dispositions, real sensor context and full-region support | **Complete for R02 raw scope:** [GR2](../artifacts/20261009T085704Z-R02/gate.md), [full input/eligibility/component tables](../artifacts/20261009T085704Z-R02/T_R02_components.md), [raw timeline](../artifacts/20261009T085704Z-R02/F_R02_raw_timelines.png), [method freeze](../artifacts/20261009T085704Z-R02/method_freeze.json). D 250/250; G 163/250 with explicit unknowns. No final reference support yet. |
| BOUNDARY | Actual changed/withheld evaluator files and future events; identical prefix scores/state plus leakage-positive control | **R02 raw operational boundary verified:** [isolation record](../artifacts/20261009T085704Z-R02/boundary_isolation.json), [92-test report](../artifacts/20261009T085704Z-R02/test_results.xml). Evaluator categories were inaccessible then changed while allowed bytes stayed fixed; raw outputs and access logs matched, positive control trapped. Future-event prefix invariance passed for raw records. Score/state boundaries remain for R03. |
| FIT | Real clean reference rows; independent clean calibration replay; no algebraically manufactured anomalies | Not run; R04 protocol and R05 execution |
| OVERLAY | Same-reader reload, intended/injected/realized ledger, failures and unchanged originals/companions | Not run; R03/R05 |
| TEMPORAL | Irregular-time recurrence, warm-up/missing/reset/recovery and contamination evidence | Not implemented; R03 |
| COMPARE | Four segment-grouped folds, all outcomes, ablations, support/coverage and uncertainty | Not run; R05 |
| HOLDOUT | mini_14 exposure log and frozen final single-segment check | Unopened; R06 |
| PAPER | Understandable figures, evidence/claim traceability, negative results and related-work assessment | Planned; R07; no novelty or publication claim |
| DEFERRED | Consensus/bandwidth/AP/learned/adaptive/transfer studies | Out of primary scope; no implicit execution |

Completing a future row requires executed notebook, visible figure/table, appropriate test report, manifest and gate links. Failed/blocked/no-power outcomes remain explicit. A test count or checksum pass cannot certify research validity.
