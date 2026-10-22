# Prompt 2 — Start a new feature-reliability research project

Copy everything below the divider into the new Agent Deck development environment. First make the entire output of Prompt 1 available there as `planning/findings/`, or supply its actual path. Existing raw data and code are optional later migration inputs, not implicit prerequisites.

---

Act as my research collaborator in cooperative LiDAR perception, statistical modeling, adversarial robustness, and efficient systems. Start a new research project from first principles. The intended final deliverables are a reproducible implementation, extensive experiments, detailed executed Jupyter notebooks, and an evidence-supported research-paper draft. Begin with extensive planning and primary-literature review. Do not jump directly into a scoring formula or implementation.

I want to work through the scientific choices with you. In this first invocation, complete the literature, feasibility analysis and concrete methodology proposal to the extent available evidence permits, then stop at a reviewable planning checkpoint. Plan later implementation, attacks, evaluation and paper writing in detail, but do not automatically launch large downloads, training, or the full study. Small disposable feasibility checks are appropriate when necessary to resolve an actual design question; label them as pilot evidence and keep them out of final evaluation.

## Research objective and inherited evidence

Our primary question is whether a lightweight receiver can estimate the time-varying reliability of received intermediate information from cooperating LiDAR agents, at a meaningful feature-region or object-evidence level, and use that estimate to preserve or improve perception under corruption.

The unit of reliability is the received information at a particular time and location/task unit. One sender can provide reliable and unreliable regions in the same message. We are moving away from a global sender reputation. Identity may identify a source and maintain separate causal state, but must not become an unexplained shortcut to reliability.

Read `planning/findings/` first, especially its standalone handoff, failure analysis, data/feature feasibility, verified results and reuse specifications. Treat it as audited historical evidence with stated limitations, not a mandatory architecture. If it is unavailable, record that gap and ask for its path while continuing independent literature work. Never invent its contents. Do not import the old repository wholesale, install its old environment by default, resume its stages, or relabel old count scores as feature reliability.

Harmful manipulation should tend to lower reliability relative to a matched clean case, but this is a hypothesis to test. Some changes are harmless, some adversarial evidence is observationally indistinguishable from honest evidence, and benign faults can make information unreliable. Do not force every attack to decrease every score, infer malicious intent from inconsistency, or hard-code favorable results. No novelty, robustness or publishability claim is assumed.

## Phase A — Clarify the scientific object and deployment contract

Write an explicit problem statement before choosing equations. Explain and keep separate:

- Raw points, engineered geometric statistics, learned intermediate feature tensors, object queries/proposals, and final detection boxes. Sending final boxes is usually a different fusion setting from exchanging intermediate tensors; do not quietly switch the research question to make the method convenient.
- Corruption detection, geometric consistency, object correctness, contribution to downstream task performance, model uncertainty, and agent honesty. They are different targets. Define which one the score estimates and which are secondary diagnostics.
- Offline training/feature caching, sender encoding, transmission, receiver decoding/alignment, reliability estimation, fusion and detection. Show the full information flow, inference trust boundary, labels-only evaluation boundary, and where the new method operates.

Specify a candidate notation and typed contract, for example received feature `z[i,t]`, spatial unit `u`, receiver evidence `e[t]`, causal history `h[<t]`, and `r[i,t,u]` with an explicit known/unknown/support status. This is notation, not a chosen formula. State whether the output is an uncalibrated consistency statistic, a rank, a calibrated probability of a defined event, or an estimate of marginal utility. A number in [0,1] is not automatically a probability. A scalar anomaly target is not automatically a feature-quality label.

Define a practical observable correctness/usefulness target. Feature tensors do not usually come with direct “correct feature” labels. Consider predeclared GT object matching, local occupancy error where justified, or controlled changes in downstream loss when a spatial feature contribution is included versus excluded. Explain the limits and expense of each, label assignment/receptive-field ambiguity, proposal dependence, missed objects, duplicate predictions, and unmatched regions. A decoded correct object does not certify every latent channel. Keep an operational feature-level output and a defensible evaluation bridge.

Resolve deployment location: sensor microcontroller, sensor-adjacent embedded computer, vehicle ECU, RSU, or another receiver. Do not assume all LiDAR devices have the same compute. If hardware is unknown, present a few provisional budget profiles and identify the one decision needed from me. Separate incremental reliability overhead from the encoder/fusion/detector cost and the offline training budget. Never claim on-sensor feasibility from a workstation benchmark or from counting only additions in the final ratio.

Ask only consequential questions that sources cannot answer: target hardware, available training hardware, permissible receiver inputs/extra messages, time budget, and whether the output may use decoded proposals. Bundle them concisely. State provisional assumptions and keep working on independent parts. Do not silently turn provisional budgets into measured facts.

## Phase B — Extensive, critical literature review

Search current primary literature and trace backward/forward citations. Cover seminal work and recent work through the actual review date. Use papers, supplementary material, official code and dataset documentation. Surveys are discovery aids. Read methods, assumptions, experiments and limitations, not just abstracts. Do not fabricate citations, implementations, checkpoints, measurements, or access to an unread paper.

Cover these connected areas:

1. Cooperative perception and actual intermediate-fusion representations, including heterogeneous sensors, alignment, communication and temporal/asynchronous settings.
2. Malicious participants, feature fabrication/perturbation, object spoofing/removal, robust fusion, and adaptive attacks against reliability defenses.
3. LiDAR ray/occupancy/free-space consistency, occlusion, inverse sensor models, object verification and multi-view geometry.
4. Lightweight statistical, Bayesian/evidential, robust-estimation and sequential-change methods; distinguish useful principles from unjustified independence assumptions.
5. Confidence calibration, uncertainty, selective prediction and reliability evaluated against perception errors or task utility.
6. Practical memory/latency limits, sparse indexing, quantization, and implementation costs for an embedded reliability module.

Useful starting leads, to verify and read critically rather than accept as endorsements:

- Sun et al., *Towards Robust LiDAR-based Perception in Autonomous Driving: General Black-box Adversarial Sensor Attack and Countermeasures* (USENIX Security 2020; CARLO/SVF): https://www.usenix.org/system/files/sec20-sun.pdf
- *On Data Fabrication in Collaborative Vehicular Perception: Attacks and Countermeasures* (USENIX Security 2024): https://www.usenix.org/system/files/usenixsecurity24-zhang-qingzhao.pdf
- *Mixed Signals: A Diverse Point Cloud Dataset for Heterogeneous LiDAR V2X Collaboration* (ICCV 2025): https://openaccess.thecvf.com/content/ICCV2025/papers/Luo_Mixed_Signals_A_Diverse_Point_Cloud_Dataset_for_Heterogeneous_LiDAR_ICCV_2025_paper.pdf
- Mixed Signals official implementation: https://github.com/acfr/Mixed-Signals-Dataset and devkit: https://github.com/quan-dao/mixed-signals-devkit
- OPV2V primary paper: https://arxiv.org/abs/2109.07644
- DAIR-V2X official repository: https://github.com/AIR-THU/DAIR-V2X

These are seed references, not an exhaustive or already-completed review. If a PDF fails to load, find a legitimate author/venue copy and mark access status. Never represent a search snippet as a full-paper reading. Verify current model/checkpoint links; historical repositories may contain placeholders or support only some fusion modes.

Create a search log with queries, dates, inclusion/exclusion rules and forward/backward citation trails; a bibliography; a method comparison matrix; and detailed reading notes for the closest relevant methods. Aim to deeply read roughly 8–12 closest papers and screen a broader set, adjusting to relevance instead of padding a quota. For each close paper record:

- Exact citation, stable URL/DOI, version and read/access status.
- Research question, reliability unit, representation and inference inputs.
- Threat model and which evidence is trusted or independent.
- Core equations/algorithm with section/page locators and your own explanation.
- Dataset, labels, splits, baseline fairness, attack realism and major limitations.
- Compute and memory evidence, and what costs were excluded.
- Code/checkpoint/license/reproduction status.
- What we could adapt, what does not transfer, and the experiment that would test the transfer.

Produce a closest-prior-work table for our candidate contribution. Attribute borrowed mathematics precisely. If the proposed support/traversal idea is substantially covered by existing work, say so. A meaningful result might instead be efficient implementation, calibrated selective reliability, a different information boundary, rigorous evaluation, or an informative failure study. Do not invent novelty by renaming a ratio.

## Phase C — Dataset, ground truth, and feature pipeline feasibility

Compare retaining Mixed Signals against at least two genuinely relevant alternatives discovered in the review, such as OPV2V, V2XSet, DAIR-V2X/V2X-Seq or V2V4Real. These are candidates to investigate, not claims that every required asset is available. Distinguish simulated and real data and independent scenes/sessions.

Build an evidence-backed decision table: annotation availability/completeness and license; agent counts and principal independence; temporal continuity; sensor origin/calibration and ray semantics; synchronization; heterogeneous sensors; feature-framework compatibility; usable pretrained encoder/fusion checkpoints; train/test provenance; installation risk; compute/storage/download cost; and alignment with our threat model. Do not abandon useful local data merely because it contains raw points, or retain it merely because we already downloaded it.

For each viable option specify the exact path from raw input to intermediate features and GT-evaluated output. Name a candidate backbone, exact extraction/injection layer, tensor axes/shape/stride/coordinate convention, normalization, compression/quantization, alignment and fusion stage. Verify these in official code/docs when possible. Separate known facts from proposed implementation choices. Pin versions and checkpoint provenance before empirical use.

A pretrained compatible feature encoder plus a small reliability module may be feasible; training an entire cooperative detector is a separate resource commitment. Check whether the pretrained model saw evaluation scenes. If checkpoint/training data provenance is unavailable, disclose the consequence. Consider offline feature caches for cheap exploration, but explain that point-cloud attacks require re-encoding, that feature-only attacks target a different surface, and that cached experiments do not establish online end-to-end latency.

Make GT validation central. GT may train the detector/reliability model, support development and calibrate a supervised reliability target using their designated splits. GT must not leak into operational inference or final test tuning. Attack schedules, masks and clean counterfactuals are evaluator inputs only. Include genuinely missing annotations, coverage limitations, coordinate/class mapping and correct treatment of unlabeled regions. Do not treat “not annotated” as known free space without justification.

Before a large attack study, require a small clean end-to-end sanity check: correct coordinates and labels, plausible predictions, nondegenerate task metrics, usable feature interface, and measured costs. The check should expose incompatibilities early. It must not become a substitute for an independent test set.

## Phase D — Candidate mathematics, including the ray idea

Compare a small number of tractable candidates. Include a deterministic support/traversal baseline if feasible, one justified statistical/evidential alternative, and a genuinely lightweight learned combiner only if data and deployment constraints support it. Include simple detector-confidence and no-reliability baselines. Do not require a complex ensemble or assume a neural model is necessary.

For every candidate define its estimand, all variables/units, inputs available at decision time, proposal/association mechanism, score equation, fitting/calibration, unknown conditions, causal state updates, theoretical properties that can actually be shown, failure cases, and full runtime/memory/communication complexity. Explain why its evidence should track the chosen target, not merely why the formula is bounded. Give falsifying cases and conditions in which two different worlds produce identical allowed inputs.

For supporting/traversing rays, investigate these issues explicitly:

- For a trusted observation origin `o` and endpoint `p`, the observed ray segment can be parameterized as `o + lambda*(p-o)`, `0 <= lambda <= 1`, subject to timing/deskew and return assumptions. Define what counts as support, contradiction, occluded/irrelevant evidence and unknown. Define distance tolerances, surface/volume geometry, angular resolution and return endpoints; do not count an entire infinite line or the outgoing/return path twice.
- A ray terminating before an object can indicate occlusion. A ray passing through a proposal envelope and returning farther away is not automatically proof the object is false: boxes contain empty space, rays can pass around non-solid shape parts, materials/multiple returns matter, and timing/pose error can misalign a moving object. State the occupancy/surface model that licenses a contradiction and test violations.
- Missing points, beams with unknown firing status, or unobserved areas are not free-space observations. Do not reconstruct unrecorded no-return rays from a convenient scanner grid unless it is explicitly an approximation with validated assumptions.
- Counts need coverage and uncertainty. Investigate smoothing or interval bounds for low support, visibility/range/angle effects, correlated nearby rays and sensor differences. A support ratio is not automatically an object-existence probability; a beta-binomial or other evidential model needs a defensible observation model and cannot assume independent rays without examination.
- Avoid self-verification: an attacker controlling features may also forge accompanying point/occupancy summaries. Distinguish sender-reported evidence from trusted receiver evidence and independently controlled peers. Authentication of a sender does not verify its claims. No overlap should cause uncertainty/abstention, not automatic rejection of an honest unique view.
- Standard intermediate feature tensors need not retain ray origins, per-return geometry or object semantics. State exactly how the receiver obtains the proposal and ray evidence: its own scan, a trusted auxiliary source, an explicit additional message, or an approximate decoded representation. Budget its cost and spoofability. If the required evidence is unavailable under the selected feature-only protocol, reject or narrow this candidate instead of covertly allowing access to all senders' clean raw clouds.
- Explain how evidence on an object/region becomes reliability of a particular received feature contribution and how it changes fusion. Handle unmatched proposals, missed objects, overlapping receptive fields, duplicate hypotheses, empty regions and multiple senders. If this is only post-detection object verification, label it accurately and explain how that changes the original objective.
- Count ray intersection, indexing, coordinate transforms, proposal extraction, memory traffic and state maintenance as well as final additions/divisions. Preprocessing shared with the existing perception pipeline may be amortized only when that assumption is measured and reported.

Consider whether temporal consistency, independently supported occupancy, cross-view residuals, robust aggregation, or a small calibrated classifier adds complementary evidence. Prevent double counting correlated signals. Freeze learning/reference updates appropriately and test history poisoning, on/off attacks, long silence, reset, recovery and stale evidence. Show both instantaneous estimates and temporal state; do not smooth away critical short failures or reset at evaluator-known attack offsets.

Finish with a reasoned shortlist, recommended minimal method, alternative if its feasibility fails, and explicit unresolved assumptions. Select based on literature and clean development feasibility, not on desired held-out attack curves.

## Phase E — Preregister experiments and evaluation

Define the full protocol before final evaluation. Separate training, development, probability calibration or operating-threshold calibration as applicable, and test. Group all agents, nearby frames, clean/attacked variants and cached features from a scene/session together. Use the broadest meaningful independence unit. Previously inspected Valid Point comparison outcomes are development evidence for new choices; they are not a fresh blind test. Preserve an exposure ledger. Do not assume an old mini_14 is an adequate or automatically authorized new test set.

Use paired clean/attacked observations while keeping the clean counterpart inaccessible to the operational method. Labels describe the underlying physical world when corrupting measurements/messages, not the attacker's fabricated world. Keep attacker knowledge separate from evaluator knowledge, and label any GT-targeted attack as such. Freeze attack selection, seeds, budgets, schedules and intended/achieved severity before test exposure.

Cover both attack surfaces separately:

1. Raw-cloud alterations before feature encoding: removal, localized insertion/ghosts, displacement, and count-preserving geometric changes where useful and physically meaningful.
2. Received intermediate-feature alterations: spatial patch replacement/suppression, bounded activation perturbation, channel corruption/scaling, stale/replayed features or alignment manipulation if permitted by the threat model. Add a targeted/adaptive attack against the reliability mechanism when feasible, not only arbitrary noise or obvious all-zero payloads. State white/gray/black-box access, compromised principals, temporal knowledge, norm/spatial/communication constraints and whether the attacker can forge side evidence.

Do not call direct tensor edits physically realizable laser attacks. Object-level manipulation must demonstrate actual downstream effect rather than assume that editing a tensor region creates or removes an object. Report intended injection, successful serialization/reload, actual feature/raw change and resulting task harm separately. Zero-effect and failed attacks remain visible.

Include clean natural variation and benign stresses: noise, quantization/compression, legitimate sparse returns, occlusion/unique views, moving objects, pose/calibration/timing error, delayed or missing observations and heterogeneous devices. Avoid rewarding a method that rejects everything or flags benign sparsity as maliciousness.

Evaluate at three connected levels:

- **Reliability behavior:** paired change, per-unit ranking/discrimination against the defined harmfulness/correctness target, severity response with uncertainty, calibration metrics only for probabilistic outputs, risk-versus-coverage/selective performance, unknown rates, and time to change/recover where meaningful.
- **Task quality against GT:** the dataset's justified 3D detection/occupancy metrics with exact classes, matching/IoU rules, range and label coverage; false objects, missed objects and localization errors; clean quality retained; and downstream quality under attack. Compare ego-only, ordinary collaboration, simple gating/confidence, the closest feasible prior method, and our reliability weighting/gating at fair resource/information budgets. Include an explicitly evaluator-only oracle diagnostic if useful. A score decline without task relevance is insufficient for a utility claim.
- **System cost:** incremental and end-to-end p50/p95 latency, throughput, peak working memory/model storage, additional communication bytes, state size, and energy only when measured. Separate disk I/O, feature extraction, reliability computation and fusion; report device, precision, threading, warm-up, batch size and power mode. If target hardware is unavailable, report proxy benchmarks and withhold deployment claims.

Define all denominators, eligibility, empty classes, abstention, preexisting alarms, censoring and failed-injection handling in advance. Distinguish false positive rate on usable decisions from all-attempt coverage. Evaluate adaptive evasion and forced abstention without hiding them. Predefine ablations for support versus traversal, visibility handling, temporal memory, candidate signals, learned versus deterministic combination, precision and resolution if relevant; avoid an unbounded combinatorial grid.

Report each scene/session and a justified aggregate. Frames, points, synthetic seeds and repeated attacks are not independent scenes. Use scene/session-level uncertainty where the population supports it; qualify tiny-group bootstrap estimates and omit unjustified confidence intervals. Separate engineering acceptance from scientific hypothesis results. An honest negative result must remain a valid study outcome.

## Phase F — Implementation, detailed notebooks and paper plan

Plan staged delivery: literature/problem contract → dataset/labels/features feasibility → minimal method → clean and controlled pilot → frozen attacks and baselines → held-out evaluation → efficiency and ablations → paper/reproducibility. Each stage needs inputs, deliverables, tests, notebook outputs, resource budget, decision criteria and failure fallback. Check scientific feasibility early so we do not spend weeks building infrastructure around an untestable objective.

Use small importable modules, versioned configurations and thin runners. Save immutable experiment records with enough provenance to reproduce claims, without unnecessary full copies of archives or source trees. Make stage reruns resumable and deterministic where appropriate. Pin compatible dependencies after selecting the actual model ecosystem; do not inherit an incompatible Python version from the old project.

Require substantial `.ipynb` notebooks for every implemented research segment, with several dedicated notebooks for complex segments such as methodology, attacks and evaluation. A reasonable starting sequence is:

1. Literature-to-hypothesis synthesis and mathematical examples.
2. Dataset/GT integrity, timing and coordinate visualization.
3. Feature extraction/alignment and clean perception validation.
4. Ray/occupancy geometry, support/contradiction, assumptions and counterexamples.
5. Reliability model derivation, hand checks, fitted parameters and calibration.
6. Temporal behavior, missingness, sparse support and benign controls.
7. Raw-cloud attack construction and realization checks.
8. Intermediate-feature attacks, targeted effects and adaptive evasion.
9. Per-scene clean/attacked visualizations and GT task results.
10. Grouped evaluation, statistical uncertainty, ablations and failure analysis.
11. Latency/memory/communication benchmarks and deployment limits.
12. Paper figures, tables, claim ledger and reproduction checks.

Adjust the notebook count to scientific segments, not cosmetic file quotas. Each completed notebook must explain its question, source inputs, equations and assumptions; show a worked example; call the actual implementation; display intermediate evidence and units; include meaningful validation and a failure/counterexample; show readable plots; and conclude with what is and is not established. Execute top-to-bottom in a fresh kernel. Include executed copies, exported figures/tables and provenance. A notebook that only displays “PASS” or links elsewhere is not sufficient, though a reporting notebook may transparently read sealed outputs.

The final paper draft should contain related work, a precise contribution statement, formal problem/threat model, method, reproducible experiments, GT-linked results, efficiency, ablations, limitations and a failure gallery. Build a claim-to-evidence ledger from the start. Distinguish previously published ideas from our contribution, simulations from real data, and demonstrated properties from conjectures. Support each table/figure with an exact generation command. Include negative findings and unrun experiments. Do not promise publication or submit externally; publication suitability is a conclusion to assess after the evidence exists.

## Files to produce during this first planning invocation

Create a coherent `planning/` package in the new project, preserving imported `planning/findings/`:

- `README.md`: reading order, current status and decisions needed.
- `research_charter.md`: objective, estimand, hypotheses, contribution candidates and non-goals.
- `literature/search_log.md`, `literature/references.bib`, `literature/comparison_matrix.csv`, and detailed `literature/reading_notes/`.
- `information_and_threat_model.md`: permitted inputs, causal/trust boundaries, attack capabilities, deployment placement and data flow.
- `dataset_and_feature_feasibility.md`: evidence-backed options, GT contract, exact feature pipeline, resource estimates and missing assets.
- `methodology_candidates.md`: mathematical alternatives, derivations, counterexamples, identifiability, complexity and selection rationale.
- `methodology_spec.md`: recommended minimal method, precise contracts and provisional/verified status of every assumption; unresolved items visibly marked.
- `evaluation_protocol.md`: labels, splits/exposure, metrics, baselines, uncertainty and falsification criteria.
- `attack_and_benign_protocol.md`: attack surfaces, budgets, realization checks and controls.
- `compute_memory_and_communication_budget.md`: end-to-end and incremental costs, hardware profiles and benchmark plan.
- `implementation_roadmap.md` and `notebook_plan.md`: staged tasks, tests, scientific gates and detailed notebook contents.
- `paper_plan.md` and `claim_evidence_ledger.csv`: intended argument and evidence required, with no invented results.
- `decision_log.md`, `risks_and_open_questions.md`, and `next_session_brief.md`: choices, alternatives, blockers and the next bounded action.

Link these documents rather than repeating the same text everywhere. Do not fill missing evidence with confident prose. Record sources and confidence for decisions, and mark proposed numeric defaults as assumptions needing development justification.

## First-invocation stopping point

Finish with an accessible explanation of what the new project would measure, the closest prior work, whether the ray idea is feasible under our information model, the recommended dataset/feature pipeline and method, why those choices fit the budget, what could falsify the method, and the few decisions that truly require my input. Provide concrete planning files and a next-session brief.

Do not simply present a vague plan and ask whether to proceed before completing the authorized review. Conversely, do not treat the intended eventual paper as permission to skip the initial scientific discussion and launch the full implementation. If essential literature, model assets, labels, hardware information or trustworthy observability are missing, state exactly what remains unresolved and narrow the proposal accordingly. Stop at the completed planning/review checkpoint so we can solidify the methodology together before development.
