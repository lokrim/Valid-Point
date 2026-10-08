# Visible evidence and reproducibility — revision 2026-10-08

Historical S notebooks/artifacts are immutable evidence at their original scope; [audit corrections](evidence_audit.md) govern interpretation. New stages use R-prefixed notebooks, never overwrite old outputs. R01–R07 prompts are invoked individually and stop after their gate.

Every implemented stage has an executed notebook in a fresh kernel: question/claim boundary; complete bounded input example and units; exact source/clock/frame/config; importable computation; raw/normalized/state records; failures and unknowns; meaningful checks; visible technical gate and separate scientific interpretation. Display actual plots inline, not only filenames. Export full tables alongside readable completeness summaries. No hidden algorithm in display code, no notebook with cached cells standing in for execution.

| Stage | Notebook(s), planned | Named evidence |
| --- | --- | --- |
| R01 | `R01_development_intake.ipynb` | T_R01_schema, T_R01_timing, T_R01_component_feasibility, F_R01_geometry |
| R02 | `R02_causal_factors.ipynb` | T_R02_inputs, T_R02_eligibility, T_R02_components, F_R02_raw_timelines, F_R02_alignment |
| R03 | `R03_replay_temporal.ipynb` | T_R03_attempts, T_R03_roundtrip, T_R03_state_checks, F_R03_geometry, F_R03_timelines |
| R04 | `R04_protocol_freeze.ipynb` | T_R04_splits, T_R04_parameters, T_R04_lineage, frozen protocol hash; no test performance |
| R05 | `R05_segment_timelines.ipynb` per C segment and `R05_grouped_evaluation.ipynb` | F_R05_timelines, F_R05_geometry, F_R05_ablations; T_R05_metrics, T_R05_coverage, T_R05_failures, T_R05_clean_support |
| R06 | `R06_final_holdout.ipynb` | T_R06_exposure, T_R06_metrics, F_R06_timelines, explicit final scope |
| R07 | `R07_paper_evidence.ipynb` | T_R07_claim_evidence, T_R07_protocol, F_R07_information_flow; rendered paper figure inventory |

Each `artifacts/<new_run>/` includes manifest, exact config/seeds, acquisition/source/member/derived SHA-256, code snapshot + dirty status, runtime/library environment, event clock/transform provenance, split/fold and fit/calibration IDs, raw/decision/state/attempt ledgers, execution logs, test reports, output hashes, executed notebooks, `gate.md` and failures. No fabricated code revision; record source snapshot if dirty. Threshold and reference lineage must resolve to actual row/cloud IDs. Keep label/attack evaluation artifacts separate from operational inputs.

Exports: figures PDF/SVG and PNG; tables CSV and readable Markdown. Names include R stage, method, segment, fold and run ID; no overwritten result. Save immutable outcomes even on execution failure. If data/artifacts remain local and Git-ignored, provide a manifest and resolvable local links; external publishing is not authorized by evidence requirements. Regeneration commands are explicit and never chain later stages.

Run only tests appropriate to changed implementation, retaining existing arithmetic tests. Planning-only revision used byte/link/consistency checks and did not rerun scientific notebooks. Future implementation must inspect every rendered figure for units, clipping, scales, failure visibility and readable legends; avoid selecting demonstration views by favorable outcomes.
