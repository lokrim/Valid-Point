# Notebook deliverables and acceptance

Every future implemented stage, including bootstrap, has a notebook executed
top to bottom from a **fresh kernel** with no manual hidden state. There are no
implemented notebooks at setup. Table/figure names below are planned names,
not links claiming outputs already exist.

## Common visible structure

1. Question, stage, track and explicit claim boundary; pass/fail criterion.
2. Inputs: show source scene/cloud or bootstrap file inventory, config, units,
   timing/deadline, IDs, seed and provenance; state what is unavailable.
3. Calls to importable Python functions. No hidden algorithms in cells, notebooks,
   display helpers or shell fragments; scripts call those same functions.
4. Raw measurement and normalized evidence tables, unknown/not-applicable reasons,
   outputs and units. Bootstrap displays structural checks, never fake science.
5. Named figures and tables with readable axes, legends, sample counts and
   source/run IDs. Show negative/failed cases alongside successful cases.
6. Hand-expected checks or meaningful tests versus observed output, uncertainty
   where applicable, limitations, and an explicit pass/fail/blocked gate.
7. Export paths/hashes and a short conclusion supported only by displayed data.

Tables cannot be only a `head()` preview that hides unknowns/failures. Show the
full small example and aggregate completeness plus the downloadable full table
for large runs. No stale-output reuse: export executed notebook, execution log,
start/end time and dependency/environment record. A run ending in error is kept
as failed evidence and is never presented as a passed notebook.

## Stage inventory

| Stage | Exact notebook deliverables under `notebooks/` | Named visible outputs and gate |
| --- | --- | --- |
| S00 | `00_bootstrap.ipynb` | T00_environment and T00_scaffold plus a simple dependency/file diagram F00_structure; package import/provenance conventions work; science not run |
| S01 | `01_synthetic_scenes.ipynb` | T01_scene_contract, T01_unknown_states, F01_scene_views; show geometry, occlusion, empty vs absent, causal clocks and held-out seed roles |
| S02 | `02_kinematics.ipynb`, `02_spatial_surplus.ipynb`, `02_availability.ipynb` | T02_kinematic_raw/F02_motion; T02_region_counts/F02_regions; T02_eligibility/F02_deadlines; each shows units, inputs, unknowns, benign/evasion failures |
| S03 | `03_clean_references.ipynb`, `03_score_and_ablations.ipynb` | T03_reference_support/F03_clean_distributions; T03_ablations/F03_threshold_ablation and F03_trust_point_count; hand cases, fallback, thresholds, point-count monotonicity and unknown coverage |
| S04 | `04_gt_free_oracle_gap.ipynb` | T04_gap_cases/F04_oracle_gap; fixed tiles vs boxes, empty/missed/merged regions and extra alarms; GT-free invariance to GT perturbation |
| S05 | `05_consensus_cases.ipynb` | T05_consensus_eligibility/F05_peer_cases; all seven case families, leave-one-out stats, quorum/conflict/unknown, collusion and honest outlier |
| S06 | `06_next_frame_bytes.ipynb` | T06_byte_ledger/F06_byte_timeline; hand-sized full serialized payloads, next-frame quotas, five byte counters, unknown/audit loop and exact-budget cases |
| S07 | `07_overlay_roundtrip.ipynb` | T07_overlay_effects/F07_overlay_geometry; intended/injected/realized comparison, immutable hashes, production-reader round trips and failed attempts |
| S08 | `08_synthetic_evaluation.ipynb` | T08_attack_metrics, T08_benign_false_alarms, T08_coverage, T08_tradeoffs, T08_policy_bound; F08_attack_curves, F08_benign_stress, F08_sweeps, F08_bandwidth_quality, F08_proxy_utility; paired uncertainty and negative results |
| S09 | `09_real_intake.ipynb`, `09_segment_timelines.ipynb`, `09_grouped_evaluation.ipynb` | T09_inventory/F09_geometry; T09_clean_strata, T09_attack_metrics, T09_ablations, T09_oracle_gap, T09_policies, T09_failures; F09_segment_timelines/F09_bandwidth_quality; every C segment and final H separately when authorized |
| S10 | `10_paper_results.ipynb` | T10_claim_evidence/T10_protocol/F10_overview and exported prior figures; show unsupported/unrun claims, uncertainty and limitations; no new method tuning |

Each parameterized S09 timeline executes from a fresh kernel for **each** segment
and track, saving separate outputs under that run. The grouped notebook reads
frozen measurements and includes all segments; no cherry-picked timeline only.
Final H is never silently included in development output. A future new stage
(learned model, temporal controller, detector or transfer) must add its own
fresh-kernel notebook specification and checklist before implementation.

## Provenance and export

Each future `artifacts/<run_id>/manifest.json` records schema and stage version,
source URL/revision and license, archive/member/cloud SHA-256, code commit or
source snapshot hash (including dirty status), package/environment versions,
exact command, config bytes/hash, seeds/RNG scheme, time mapping, frame/transform
IDs, track, split/fold roles, reference/calibration lineage, policy/attack IDs,
input/output hashes, failures and execution times. `config.json`, `seeds.json`,
`measurements.csv`, `metrics.csv`, `execution.log`, `gate.md`, and executed
notebooks live alongside it as applicable. Do not fabricate a Git commit if the
scaffold is not yet initialized as a Git repository.

Figures in `reports/figures/F<stage>_<name>.{pdf,svg,png}` and tables in
`reports/tables/T<stage>_<name>.{csv,md,tex}` carry sidecars linking the run,
configuration, inputs and producing notebook section. Stage/track/segment/fold
suffixes prevent overwrites. Export only appropriate formats (e.g. a table's
CSV and at least one readable form). Figures/tables and artifacts are ignored
in Git; source notebooks and configs are versioned. Keep versioned source
notebooks free of generated cell outputs; the fully executed, visible copies
belong in the immutable ignored run bundle. Share a content-addressed
run bundle or verified artifact URL so the reviewer can open actual evidence.

A completed checklist row requires a link to the executed notebook, named
figure/table, test report where relevant, and manifest/gate report. A code path,
empty figure placeholder, unexecuted notebook or undocumented assertion does
not count. Keep pending links labeled “planned” until files exist. Publish no
data or output externally merely to satisfy a link; packaging/sharing is a
separate authorized action.
