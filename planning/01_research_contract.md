# Research question and claim contract — revision 2026-10-08

**Question:** Under an explicit receiver information model, which deterministic point removal, displacement, count-preserving rearrangement and addition interventions on real Mixed Signals clouds change an explainable conformity score, at which severities, with what benign false alarms, coverage, onset delay and recovery?

H1: clean recorded observations remain relatively conforming under clean-fitted references. H2: some interventions lower conformity relative to matched clean replay; effects depend on geometry, magnitude and evidence availability. H3: temporal accumulation changes persistence, false alarms and delay relative to a memoryless baseline. H4: benign viewpoint/scene changes and information limitations explain important false alarms and non-identifiability. None is hard-coded or required to pass a technical gate. A high score means the available checks found little deviation from their reference, not a probability of honesty or a certificate of point integrity.

## Experiment and threat boundary

Base observations are immutable recorded clouds. An evaluator creates deterministic derived copies for one compromised physical vehicle per episode. Primary selected sender is `003` if present; a metadata-only fallback to the first available vehicle (`004`, then `laser`) is recorded before outcome inspection. Other agents remain byte-identical. `top` is the receiver observation; `dome` shares the RSU security principal. Initial study is four physical principals, five sensor streams when present, not five independent votes.

Primary adversary controls its own XYZ records and point count in declared windows; intensity is preserved for retained points and explicitly assigned for additions. Identity, source time, poses and calibration remain unchanged in the primary point-only experiment. This isolates point integrity. Authentication and receipt logging are modeled assumptions, not measurements in the archive. Optional pose/time spoofing requires separately verified fields and a new threat version; those claims cannot be inferred from point-only results. Attacker cannot change other streams, trusted receiver state, frozen references, or base files.

The receiver may use only decoded arrived clouds, causal history from that replay, predeclared sensor/principal identity, declared timestamp mapping, valid causal poses and fixed calibration available by the decision time. Poses from this offline recording are assumed available causally in the modeled receiver; possible offline localization corrections are a limitation, not proof of deployed availability. Metadata under sender control is not independent corroboration.

**GT-free operational boundary:** scorer, reference-context lookup and temporal state receive no labels, GT boxes, object counts from labels, attack flags, schedules, masks, clean counterpart clouds, injection success or evaluator outcomes. The offline fitting harness selects clean training observations, but passes operational raw inputs through the same reader and scoring path; the inference API never takes a `clean` flag. Evaluator data is joined only after decisions and state histories have been sealed and hashed. Synthetic arrival generation is upstream of the scorer and recorded as an assumption, not real network telemetry.

Separate records: raw measurements with units/provenance; normalized factor anomalies; instantaneous `A` and conformity `C=1-A`; temporal state `Z` and temporal conformity `C_time=1-Z`; alarm/abstention with threshold ID; evaluator-only outcomes and interval annotations. Unknown is null with a reason, never a zero anomaly. Structural not-applicable factors are frozen per method/sensor, not dropped per frame to improve scores.

## Allowed conclusions

| Evidence level | Allowed claim | Not licensed |
| --- | --- | --- |
| Existing unit fixtures | Exact arithmetic, geometry, explicit counterexamples | Dataset detection, scene independence, boundary completeness |
| R01 single development archive | Inspected fields, timing/frame feasibility and bounded geometry | Generalization or calibrated false-alarm performance |
| R02/R03 development replay | Working causal pipeline and illustrative real-cloud trajectories | Held-out effectiveness; publishability |
| R05 frozen comparison segments | Conditional recall/FPR/coverage and temporal effects for stated scenes/interventions | Intent identification, physical attack realism, robust deployment |
| R06 final mini_14 | One untouched final check of a frozen method | Broad independent-scene or cross-dataset validation |

Removal can be indistinguishable from occlusion, sparse sampling or sensor failure. Missing packets, empty clouds and absent peer support cannot establish maliciousness. Jointly consistent spoofing may pass all self-consistency checks; plausible fake structure may resemble real moving objects. Attacked history can become a misleading reference. Expose these failures without inventing unobserved visibility.

Bandwidth policy, transmission savings, detectors/AP, learned combiners, mandatory oracle-box studies, peer voting, collusion/Sybil and broad adaptive attacks are secondary and deferred. H003's quota objective and mandatory K/S/oracle architecture are superseded by H011 in [history](history.md). No publication, deployment or favorable scientific result is promised.
