# Evidence-based acceptance checklist

Status key: **Verified setup** = documentary/structural evidence only;
**Pending** = not implemented or run; **Blocked** = unmet prerequisite;
**Failed** = observed technical failure; **Negative result** = completed valid
experiment without claimed benefit. No scientific item is currently complete.

Planned paths below are names of future evidence, not assertions that files
exist. On completion replace them with links to the executed notebook, named
figure/table, test report, run manifest and gate report. Tests without visible
results, code alone and unexecuted notebooks never complete scientific rows.

| ID | Verifiable acceptance item | Status | Evidence / required future proof |
| --- | --- | --- | --- |
| P01 | Required directories and importable empty package, minimal dependency-free runtime packaging | Verified setup | [setup verification](setup_verification.md), [README](../README.md), [pyproject](../pyproject.toml) |
| P02 | Raw data and generated outputs ignored, placeholder instructions retained | Verified setup | [setup verification](setup_verification.md), [.gitignore](../.gitignore) |
| P03 | Official segment archive packaging and candidate entries checked without raw downloads | Verified setup | [sources](sources.md) |
| P04 | All user requirements mapped and eleven future prompts prepared; no research executed | Verified setup | [coverage](requirements_coverage.md), [prompt index](prompts/README.md), [setup verification](setup_verification.md) |
| P05 | Researcher reviews proposed method/resource choices before implementation | Pending | Researcher response recorded in history; G0 |
| B00 | Fresh bootstrap notebook visibly proves environment, package origin and export convention | Pending | NB00; T00_environment; F00_structure; `tests/test_bootstrap.py` report; manifest |
| C01 | Synthetic clocks/frames/seed groups deterministic and no future inputs | Pending | NB01; T01_scene_contract; F01_scene_views; `test_contracts.py`, `test_synthetic.py` |
| C02 | Empty, absent, late, malformed, inapplicable and unknown states distinct | Pending | NB01/NB02 availability; T01_unknown_states/T02_eligibility; `test_availability.py` |
| E01 | Kinematic units, motion residual and consistent-spoof evasion shown | Pending | NB02 kinematics; T02_kinematic_raw/F02_motion; `test_kinematics.py` |
| E02 | Surplus uses fixed regions; zero/occlusion is not dishonesty; addition monotonicity | Pending | NB02 spatial/NB03; T02_region_counts/F03_trust_point_count; `test_spatial.py`, `test_scoring.py` |
| E03 | No group point-share corroboration or missing-factor perfection | Pending | NB03 score; T03_ablations; `test_scoring.py` plus source review |
| R01 | Clean references training-only, support/fallback/degen cases visible | Pending | NB03 references; T03_reference_support/F03_clean_distributions; `test_references.py` |
| R02 | Separate clean calibration, frozen threshold/ties, achieved FPR and abstention | Pending | NB03 score; F03_threshold_ablation; `test_calibration.py`; reference/calibration lineage |
| R03 | Weight-free max combiner hand cases, K/S ablations and uncertainty | Pending | NB03 score; T03_ablations; `test_scoring.py` |
| G01 | GT-free score/quota unchanged by withheld or permuted evaluator GT | Pending | NB04/NB06; T04_gap_cases; `test_gt_isolation.py`, `test_bandwidth.py` |
| G02 | Oracle gap includes missed, extra-alarm, proposal and empty-region failures | Pending | NB04; F04_oracle_gap/T04_gap_cases; `test_regions.py` |
| G03 | Failed GT-free viability explicitly blocks operational claim | Pending | NB04 gate report + history; T10_claim_evidence |
| Q01 | Leave-one-out independent quorum/comparability; conflict/insufficiency unknown | Pending | NB05; T05_consensus_eligibility; `test_consensus.py` |
| Q02 | One attacker, two colluders, honest conflict, missing/membership, unique honest and Sybil/correlation cases | Pending | NB05; F05_peer_cases; scenario-completeness test/report |
| Q03 | Point addition cannot improve fixed-peer penalty; colluder-shift evasion visible | Pending | NB05; monotonic sweep and counterexample; `test_consensus.py` |
| W01 | Next-frame effective quotas and no retroactive transmission credit | Pending | NB06; F06_byte_timeline/T06_byte_ledger; `test_bandwidth.py` |
| W02 | Five byte counters reconcile with actual serialization and trusted-hop assumptions | Pending | NB06; T06_byte_ledger; `test_serialization.py` |
| W03 | Uniform/hard/linear/smooth/unknown compared at equal actual bytes; unused budget explicit | Pending | NB06/NB08; T08_tradeoffs; `test_bandwidth.py`, `test_evaluation.py` |
| W04 | Partial-cloud unknowns, audit cost, score expiry, reserve abuse and harmful packing visible | Pending | NB06/NB08; F06_byte_timeline/F08_bandwidth_quality; closed-loop tests |
| W05 | Proxy utility and hindsight policy bound distinguished from AP | Pending | NB08; T08_policy_bound/F08_proxy_utility; `test_proxy.py` |
| A01 | Original hashes unchanged; seeded overlay replay order-independent | Pending | NB07; T07_overlay_effects; `test_overlays.py` |
| A02 | Production-reader reload validates fields, coordinates, counts and hashes | Pending | NB07; F07_overlay_geometry; `test_pointcloud_io.py`, `test_overlays.py` |
| A03 | Intended/injected/realized ledger retains failed attempts and honest companions | Pending | NB07/NB08; T08_coverage; `test_evaluation.py` |
| V01 | All attack/benign/intensity/fraction/adaptive cases reported with abstention denominators | Pending | NB08; T08_attack_metrics/T08_benign_false_alarms/T08_coverage; completeness report |
| V02 | AUROC/AUPRC/recall/frozen FPR/precision at stated prevalence, undefined cases visible | Pending | NB08; F08_attack_curves; `test_metrics.py` |
| V03 | Paired seed and grouped segment uncertainty without frame pseudoreplication | Pending | NB08/NB09; intervals/counts in metric tables; `test_metrics.py` |
| D01 | Archive/time/labels/transforms verified for a bounded real sequence | Pending | NB09 intake; T09_inventory/F09_geometry; `test_mixed_signals.py` |
| D02 | >=4 distinct labeled comparison segments beyond development; additional final reserved | Pending | NB09; frozen `configs/segment_roles.json`, T09_inventory; `test_splits.py` |
| D03 | Four outer folds fit only clean other segments; no agent/frame/variant leakage | Pending | NB09 grouped; fold manifests/T09_ablations; `test_splits.py` |
| D04 | Every segment clean/attacked timelines plus aggregate and wide uncertainty caveat | Pending | Executed NB09 timelines per C0–C3; F09_segment_timelines/T09_failures |
| D05 | Real policies use GT-free score and exact bytes; no oracle/GT policy leakage | Pending | NB09 grouped; T09_policies/F09_bandwidth_quality; `test_gt_isolation.py` |
| D06 | Final H opened only after freeze; no outcome-driven scene replacements | Pending | Exposure log, final manifest, executed final NB09 outputs |
| N01 | Every implemented stage runs fresh kernel, displays failures, exports provenance and gate | Pending | All stage notebook/execution logs/manifests; `scripts/execute_notebooks.py` report |
| P10 | Paper claims linked to artifacts, all pending gates and limitations visible | Pending | NB10; T10_claim_evidence/T10_protocol; `test_reporting.py` |
| X01 | Temporal/probability/detector/transfer claims remain gated until independent evidence | Pending | New spec/notebook if invoked; otherwise explicit not-run rows in T10_claim_evidence |

At every future stage, update [history](history.md), [progressplan](progressplan.md)
and this checklist. Preserve failed/negative evidence links when a later run
passes; do not overwrite the research record.
