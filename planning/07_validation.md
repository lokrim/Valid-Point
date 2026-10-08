# Frozen evaluation and denominators — revision 2026-10-08

Primary unit is an attempted `(segment, episode, principal, sensor, acquisition event)`; temporal event-level results are supplemented by episode outcomes. Points, consecutive frames, seeds and interventions on the same base scene are **not independent trials**. Final comparison uses the segment folds in [02](02_data_protocol.md). One development archive is feasibility evidence only.

## Predictions before evaluator joins

Freeze method/contexts/engineering settings and attack grid in R04 before comparison outcomes. Process independent clean fit and calibration observations through actual reader/eligibility/raw factors/score/state. Every factor combination and temporal arm gets its own clean threshold; use the declared alpha=.01 target without claiming an achieved future bound. No attack-assisted calibration, algebraic residual construction, shared fitted global cache, threshold adjustment on outer clean outcomes or silent scene replacement.

Seal prediction/state/eligibility files and hashes before evaluator loads labels, clean counterparts, masks or windows. The evaluation layer alone joins those inputs. Inference must remain invariant when evaluator files are inaccessible or replaced; tests must actually invoke this boundary with those changed inputs. Future-event perturbation must not alter any prefix decision. A leakage-positive control must fail the test so an unexercised test cannot pass vacuously.

## Required outputs

- Geometry: matched clean/attacked native and common-frame views, metre axes, crop/target/changed rows (evaluator only), same display bounds. Show a failure as well as any visible change.
- Timelines in elapsed **seconds** for selected agent and every honest companion: raw D cell counts/G distances, normalized factor anomalies, A, C, Z, C_time, thresholds, alarms, warm-up/unknowns, pose age and acquisition gaps. RSU sensor traces remain distinct with shared-principal label. Attack onset/offset are evaluator annotations only.
- Tables: per-family/severity outcomes, clean and benign-stress false alarms, honest-companion effects, all-attempt coverage, abstention reasons, detection/recovery, component/temporal ablations, and failure gallery. Include every selected segment plus aggregate; final H separate.

## Metrics

| Metric | Numerator / denominator; units; undefined handling |
| --- | --- |
| Eligible coverage | Known decision count / all attempted event decisions; %, separated for factors, instantaneous arms and post-warm-up temporal alarms |
| Abstention | Unknown/unavailable alarm decisions / all attempted decisions; reasons include warm-up, unsupported reference, malformed/reader rejection, pose/gap/clock issues |
| Clean FPR | Alarmed clean decisions / known alarm-eligible clean decisions; also alarms / all clean attempts and time eligible. Zero eligible => undefined, never 0% |
| Benign-stress FPR | Same, separately per named benign stress and severity; no pooling into normal calibration after seeing results |
| Event recall | Alarms during a scheduled nonzero-severity intervention / all scheduled attacked event attempts, including failed injections/rejection/abstention as undetected. Also eligible-only recall and realized-nonzero reader-valid recall, each with explicit counts |
| Episode recall | Episodes with >=1 known alarm inside attack interval / all attempted attacked episodes; report intended and realized-nonzero episode populations separately. Alarm already active at onset flagged as preexisting, not newly detected |
| Delay | Seconds from first attempted onset (also first realized change as separate field) to first new eligible alarm within window. Preexisting alarm, failed injection/no exposure, no eligible coverage, and no detection have distinct statuses; non-detections are right-censored at offset/end, not dropped or assigned zero |
| Recovery | For episodes alarmed during intervention: seconds after last intervention offset until eligible non-alarm persists for 2 s with no gap >g_reset and no unknown/reset. Compute post-offset persistence offline; scorer has no offset access. Never-alarmed => not applicable; gap/reset/end without persistence => undefined or right-censored with reason |
| False-alarm episodes | Count clean alarm-run onsets separated by >=2 s of eligible non-alarm / observed clean eligible agent-minutes; also total attempted agent-minutes/unknown time. Short records give descriptive unstable rates |
| Paired effect | Attacked minus clean raw/anomaly/conformity for matched event keys; units as factor or dimensionless. Only paired known values numeric; unmatched/unknown counted separately |
| Optional AUROC/AUPRC | Known anomaly scores with target “scheduled intervention vs clean”, explicit family/severity and prevalence; one class or no support => undefined. Secondary to frozen-threshold metrics; no points-as-samples inference |

Do not mix zero-severity identity controls with positive attacks. Benign sensor degradation and removal may generate identical observations; scorer invariance to their evaluator labels is required. Reader rejection may be an input-validation outcome but never a successful score alarm. Intervention metadata cannot create a temporal decline. Report all intended episodes, affected events, feasible injections, valid reloads, realized changes, known decisions and alarms in a reconciled flow table; no denominators hidden in footnotes.

## Ablations and uncertainty

Required: D-only, retained G-only, max(D,G), and memoryless versus EWMA for each feasible arm, with separately calibrated thresholds and all-attempt/common-support results. If G is infeasible, show blocked cells instead of silently removing the comparison. Signed density/occupancy change is diagnostic; optional X/intensity/K factors need pre-freeze amendments. Changing history policy or tau is a named, recalibrated ablation, never a replacement selected after tests.

Display C0–C3 individually and equal-weight macro estimates, with frame-weighted micro estimates labeled separately. Preserve clean/attack pairings and entire episode/scene groups in uncertainty calculation. With four segments, show range and leave-one-segment sensitivity as primary uncertainty descriptions; an optional fixed-seed 2,000-resample cluster bootstrap must be labeled unstable/descriptive and resample the broadest identifiable acquisition group. Adjacent same-session segments do not become independent through fold assignment; if there is only one independent session, do not give a between-session confidence interval. Cross-fold fits share data, so model fits are not four independent repetitions. Within-segment temporal blocks may describe variability but cannot replace scene-level uncertainty. Undefined per-scene metrics remain undefined; macro rows disclose contributing scenes and omissions.

For mini_7: raw trajectories and counts only, no empirical generalization/FPR guarantee. For final mini_14: a single final check, no independent-scene confidence interval. No favorable hypothesis is required for technical completion. Preserve negative effects, tied/constant scores, no-power thresholds, calibration failure and all-abstain methods.
