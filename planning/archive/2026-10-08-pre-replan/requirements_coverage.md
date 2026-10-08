# Requirement-to-plan coverage audit

This checks documentary coverage, not empirical fulfillment. All scientific
work remains pending in [checklist](checklist.md). Numbered categories follow
the researcher's brief; “proof” here means the specification exists, not that
its future outcome is known.

| ID | Requirement | Planning location | Future stage / acceptance |
| --- | --- | --- | --- |
| SET1 | New Valid Point / valid-point / valid_point; minimal empty importable package | [README](../README.md), [setup verification](setup_verification.md) | P01 |
| SET2 | Required directories, short README, minimal packaging/config, ignored data/artifacts | [README](../README.md), [.gitignore](../.gitignore), [setup verification](setup_verification.md) | P01–P02 |
| SET3 | No algorithms/notebooks/install/download/attacks/simulations during setup | [setup verification](setup_verification.md), [history](history.md) | P04 |
| SET4 | Historical lidar-shield is read-only challenge context, no inherited code/milestones/requirements | [context review](context_review.md) | All prompts |
| REC1 | Exact history.md, progressplan.md, checklist.md; dated decisions, dependencies, risks, verifiable evidence | [history](history.md), [progressplan](progressplan.md), [checklist](checklist.md) | Every prompt requires all three updates |
| RQ1 | Sender/frame/deadline and causal information, raw/evidence/score/state/policy separation | [research contract](01_research_contract.md), [Phase 1 schemas](03_phase1_evidence.md) | C01, E01–E03 |
| RQ2 | Points/messages/timestamps/self-odometry attacker; identity/receiver-clock protection | [research contract](01_research_contract.md) | S01/S07/S08 |
| RQ3 | Benign faults, occlusion, delays/absence, add/remove/rearrange, consistent spoof, collusion/Sybil | [threat cases](01_research_contract.md), [attack matrix](06_attack_simulation.md) | Q02, A03, V01 |
| RQ4 | Bounded conformity, high score not proof, no honesty/usefulness probability | [research contract](01_research_contract.md), [claim gates](09_decisions_and_gates.md) | R03, P10, X01 |
| DATA1 | Verify official packaging; mini_7/mini_10 archives, no individual PCD downloads or assumed local archive | [sources](sources.md), [data protocol](02_data_protocol.md) | P03, S09 |
| DATA2 | One archive at a time; labels/time/transform checks, missing versus empty labels | [data protocol](02_data_protocol.md) | D01 |
| DATA3 | FOUR distinct labeled comparison segments beyond dev, roles before outcomes | [role table](02_data_protocol.md) | D02 |
| DATA4 | Each segment held out once; clean fitting/calibration inside other segments; additional final holdout | [fold table and freeze](02_data_protocol.md) | D03, D06 |
| DATA5 | Keep all agents/frames/clean/attack variants grouped; report every segment and aggregate | [data protocol](02_data_protocol.md), [statistics](07_validation.md) | D03–D04 |
| DATA6 | <4 real segments incomplete, no result-based replacement, wide generalization uncertainty | [data protocol](02_data_protocol.md), [gates](09_decisions_and_gates.md) | D02, D04, P10 |
| P11 | Kinematics, positive surplus, leave-one-out disagreement: units/data/independence/detection/confounders/evasions/unknowns | [factor table](03_phase1_evidence.md) | E01–E03, Q01 |
| P12 | Freshness/missingness/transforms/health as eligibility; empty versus absent | [schemas/factors](03_phase1_evidence.md) | C02 |
| P13 | No zero-point dishonesty, point-share corroboration or unavailable-perfect K | [Phase 1](03_phase1_evidence.md) | E02–E03 |
| P14 | NO manually fixed factor weights; max anomaly baseline, peer diagnostic/gated ablation | [score contract](03_phase1_evidence.md), [consensus](04_consensus.md) | R03, Q01–Q03 |
| P15 | Later adaptive/learned training-only monotonic constrained parameters, separate calibration, fair baseline, not universally optimal | [Phase 1](03_phase1_evidence.md), [GL gate](09_decisions_and_gates.md) | X01 |
| P16 | Engineering/reference/calibration/policy layers, clean fits, sparse fallback/abstention, frozen choices | [Phase 1](03_phase1_evidence.md), [data protocol](02_data_protocol.md) | R01–R02 |
| P17 | Equations/pseudocode, schemas, reason codes, hand cases and component ablations | [Phase 1](03_phase1_evidence.md) | R01–R03 |
| GT1 | TWO tracks from start: oracle boxes and GT-free receiver tiles/ego-only geometry | [two-track plan](03_phase1_evidence.md) | G01–G02, S04 |
| GT2 | Proposal errors, empty regions, association and changing content; GT evaluator-only | [GT-free track](03_phase1_evidence.md) | G01–G02 |
| GT3 | Real Phase 2 GT-free only, oracle gap including misses/false alarms, negative viability result | [Phase 1](03_phase1_evidence.md), [bandwidth](05_bandwidth.md), [G3](09_decisions_and_gates.md) | G03, D05 |
| GT4 | Detector later independent gate, ordinary Python first | [gates](09_decisions_and_gates.md) | Every prompt, X01 |
| CON1 | Leave-one-out independent identities, contextual normalization, quorum and verified timing/transform/view comparison | [consensus](04_consensus.md) | Q01 |
| CON2 | Correlation, shared occlusion, colluders, honest unique view; majority≠truth | [consensus cases](04_consensus.md) | Q02 |
| CON3 | One attacker/two colluders/conflicting/missing/changing peers; unknown failures and point-addition test | [consensus](04_consensus.md) | Q02–Q03 |
| BW1 | Uniform/hard/linear/smooth/unknown policies under same total and actual bytes | [bandwidth](05_bandwidth.md) | W03 |
| BW2 | T=.4 quota experimental, conformity≠view utility, byte fraction≠impact fraction | [bandwidth](05_bandwidth.md) | W03–W05 |
| BW3 | Payload units, serialization costs, adversarial harmful packing | [byte/payload contracts](05_bandwidth.md) | W02, W04 |
| BW4 | Full f observation controls f+1, five byte counters, link enforcement vs receiver dropping | [timing/ledger](05_bandwidth.md) | W01–W02 |
| BW5 | Synthetic task/corruption proxy, no invented AP/fusion results; censoring/audit feedback explicit | [bandwidth](05_bandwidth.md), [validation](07_validation.md) | W04–W05, X01 |
| AT1 | Seeded immutable overlays, no original mutation, all requested attack/benign families | [attack matrix](06_attack_simulation.md) | A01, V01 |
| AT2 | Oracle and GT-free targets; intended/injected/realized effects, failed attempts and honest companions | [overlay contract](06_attack_simulation.md) | A03 |
| AT3 | Production-reader reload of fields/coordinates/counts/hashes; synthetic first; gated bounded real sequence | [reader gate](06_attack_simulation.md) | A02, D01 |
| VAL1 | Clean distributions/FPR by sender/segment/range/object count/missingness and benign stress | [validation matrix](07_validation.md) | V01, D04 |
| VAL2 | Per-attack AUROC/AUPRC/recall at benign FPR/prevalence precision, abstention and coverage | [metrics](07_validation.md) | V01–V02 |
| VAL3 | Intensity/fraction/collusion/adaptive sweeps; temporal only after controller | [validation](07_validation.md), [GT gate](09_decisions_and_gates.md) | V01, X01 |
| VAL4 | Reference/threshold/component ablations and oracle gap | [validation](07_validation.md) | R03, G02, D03 |
| VAL5 | Equal-byte policies, quality/influence/honest-view curves, LOO PROXY and hindsight POLICY upper bound | [bandwidth](05_bandwidth.md), [validation](07_validation.md) | W03–W05 |
| VAL6 | Per-segment results, grouped uncertainty, failed cases, reproducible figures/tables | [statistics/paper exports](07_validation.md), [notebook contract](08_notebooks.md) | V03, D04, P10 |
| VAL7 | ECE/reliability need probability target; AP@0.5/0.7, detector utility, ROBOSAC/MADE, transfer later gates | [matrix](07_validation.md), [gates](09_decisions_and_gates.md) | X01 |
| NB1 | Every stage fresh kernel, visible inputs/measurements/unknowns/outputs/failures/conclusions, importable computation | [common contract and stage inventory](08_notebooks.md) | N01, all prompts |
| NB2 | Scenes, each factor, references, point-count trust, consensus, per-segment timelines, thresholds, exact-byte timelines and trade-off curves | [notebook inventory](08_notebooks.md) | All stage notebook rows |
| NB3 | Report-ready figures/tables/config/seeds/provenance; no completion by code alone | [export contract](08_notebooks.md), [checklist](checklist.md) | N01, P10 |
| PR1 | Eleven ordered self-contained prompts, prerequisites, exact files/notebooks, visible outputs, tests, provenance, all records, stop/go | [prompt index](prompts/README.md) | P04 |
| STOP | Summary, genuine decisions, stop at review before implementation | [decisions](09_decisions_and_gates.md), [progressplan](progressplan.md) | P05 remains pending |

Coverage review conclusion: every requested category has a concrete document
and/or staged prompt. This says nothing about whether H1–H4 will be supported.
