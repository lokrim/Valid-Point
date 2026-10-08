# Validation matrix, statistics, and paper artifacts

All entries are planned, not achieved. S = synthetic Python; R = four-or-more
labeled comparison segments with frozen outer evaluation; D = separately gated
genuine detector/fusion path. A toy or oracle-box result cannot satisfy D.

## Comprehensive comparison matrix

| Study / primary outcome | S | R | D / restriction | Planned export |
| --- | --- | --- | --- | --- |
| Clean T/K/S distributions, benign FPR and abstention by sender, segment, range, object count and missingness | Controlled truth and scene strata | Per-segment strata; GT object count evaluator-only | No probability claim | F03_clean_distributions; T03_reference_support; T09_clean_strata |
| Benign dropout, delay, noise, miscalibration, occlusion, dense scenes | Controlled fault sweeps | Replay overlays plus observed missingness, separately labeled | Fault≠malice | F08_benign_stress; T08_benign_false_alarms |
| Per-attack AUROC/AUPRC, recall at fixed benign FPR, prevalence-specific precision | Held-out seeds and all attempted cases | Held-out segments, oracle and GT-free separately | No malicious-intent target inferred from score | F08_attack_curves; T08_attack_metrics; T09_attack_metrics |
| Intensity, compromised fraction, collusion and threshold-aware sweeps | Full declared grid | Supported bounded sequences; explicit failures | Adaptive attacker knowledge fixed | F08_sweeps; T08_coverage |
| Temporal detection, alarm delay, recovery and false episodes | Only after controller gate | Only after controller and timing assumption gates | Deferred for instantaneous baseline | F08_temporal_optional; T08_temporal_optional |
| K-only, S-only, K/S and gated-P ablations; reference/threshold sensitivity | Common support and all decisions | Per-fold fitting/calibration; no outer tuning | Learned combiner optional gate | F03_threshold_ablation; T03_ablations; T09_ablations |
| Oracle boxes versus fixed tiles / ego proposals | Misses, extra alarms, unknowns, empty/merged regions | Paired held-out units, coverage-adjusted gap | Oracle is not operational path | F04_oracle_gap; T04_gap_cases; T09_oracle_gap |
| Consensus: conflict, collusion, missing peers, changing membership, unique honest view | Required full case table | Only valid comparable independent views | No majority-truth assumption | F05_peer_cases; T05_consensus_eligibility |
| Hard/linear/smooth/uniform/unknown policies at equal actual bytes | Closed-loop, audit and harmful packing | GT-free scores and exact modeled transport | Receiver-only drops cannot claim network savings | F06_byte_timeline; T06_byte_ledger; T09_policies |
| Bytes versus task-quality proxy, attack influence and honest-view loss | Paired seed quality curves | Label/support proxy, honest companionship, per segment | Not real AP/fusion gain | F08_bandwidth_quality; F09_bandwidth_quality; T08_tradeoffs |
| Leave-one-agent-out PROXY utility, useful honest outlier and hindsight oracle POLICY bound | Finite exact/bounded toy evaluator | Proxy comparator only unless bound proven | Not detector-based utility | F08_proxy_utility; T08_policy_bound |
| Per-segment clean/attacked timelines and failure gallery | Synthetic per episode | All four C segments, plus final H only after lock | Include blocked/unknown cases | F09_segment_timelines; T09_failures |
| Probability reliability / ECE | Deferred until binary target + fitted probability + separate calibration | Same plus grouped external evaluation | Never plot T as honesty probability | Future independent protocol |
| AP@0.5/0.7, actual fusion gain and detector-based leave-one-agent-out | Insufficient | Insufficient with boxes/proxy alone | Real model, checkpoints, label protocol, comparable costs and genuine inference required | Future independent D study |
| ROBOSAC/MADE comparisons and cross-dataset transfer | Insufficient as toy replicas | Not licensed by same-scene score results | Verified methods, comparable threat/budget/task, independent dataset gate | Future independent D/transfer study |

## Metric targets, coverage, and denominators

The initial binary evaluation target is **injected attack attempt versus clean
observation**, with benign faults as a separate negative stress population.
It is not “honest person versus malicious person.” Keep attack family and
realized-effect target separate. AUROC/AUPRC use anomaly `A=1-T` only for known
scores, disclose excluded counts, and are undefined when a comparison contains
one class. AUPRC depends on prevalence; do not compare unlike mixtures silently.

Report for every family/severity/segment: intended attempts, feasible injections,
reader-valid cases, eligible known scores, abstentions by reason, realized
nonzero effects, scored-case recall, all-attempt recall (unknowns count as
undetected), and realized-effect recall with its distinct denominator. None can
replace the others. Removal/count-preserving attacks remain in coverage and
failure tables even when unsupported; absence of a supported detector is not
hidden by dropping those attacks from the study.

Freeze alpha=1% as proposed in the score contract. Thresholds are selected on
clean calibration only; report test recall **at that frozen operating point**
and achieved test FPR, never retune on held-out clean frames to force 1%.
Precision is shown at explicit designed prevalences 1%, 10%, and 50%, using
`p*TPR / (p*TPR + (1-p)*FPR)` where estimable, with uncertainty and target
population stated. Also show empirical precision for the actual replay mix.
No division-by-zero defaults; undefined cells remain named unknown.

Report harmful admissions, honest bytes suppressed, unique-honest-view loss,
starvation duration and unknown reserve abuse per policy. Calibration FPR,
benign stress alarms and honest companions wrongly deprived of data are
different outcomes. Small score FPR does not establish acceptable policy loss.

## Statistical reporting

- Primary aggregate: equal-weight mean of the four segment estimates. Show
  each segment first, spread/range and the micro/frame-weighted result separately.
  Pooling millions of correlated points is not a sample-size argument.
- Pair clean/attack variants and policies on the same scene, seed, sender and
  byte conditions; preserve the entire pairing in resampling. Synthetic
  uncertainty resamples independent scene seeds, not points or frames.
- Real uncertainty uses segment-grouped bootstrap of whole paired outcomes
  (proposed 2,000 resamples, fixed resampling seed), with 95% intervals explicitly
  labeled descriptive and unstable with four groups. Show all four estimates
  and leave-one-segment sensitivity. Fold fits overlap, so do not claim four
  independent model fits or precise population coverage. If acquisition groups
  reveal fewer independent sessions, report that limitation and resample at the
  broader group where feasible; a single session cannot estimate session-level
  generalization.
- Within-segment temporal-block intervals are secondary descriptions, not
  substitutes for between-segment uncertainty. Freeze a physical block duration
  from development autocorrelation before held-out analysis. Record the choice.
- Show sample counts, unknowns, class balance, raw effect differences, intervals,
  and units in each table. Do not report favorable maxima across seeds or
  selective “representative” scenes. Predeclare H1/H2/H3 as primary; sweeps and
  extra comparisons are exploratory. If p-values are later used, declare the
  family and multiplicity correction before seeing results.
- Log numerical instability, zero-support bins, missing strata and failed
  injections. No fabricated curves for blocked, unrun, or undefined cells.

## Paper narrative and exports

The eventual paper should connect the threat/information diagram, raw factor
examples, clean reference plots, injection-count versus trust, oracle-gap maps,
consensus failures, per-segment timelines, threshold/ablation comparisons,
exact-byte timelines and bandwidth–quality curves. Include a dedicated failure
table with count-preserving attacks, consistent odometry spoofing, honest unique
views, sparse references and uncertain transforms even if performance is poor.

`T10_claim_evidence` maps each sentence-level claim to track, run, notebook cell,
figure/table, denominator and scope limitation. `T10_protocol` lists splits,
sources, seeds, fitted references/calibration and byte assumptions.
`F10_overview` is a method/information-flow diagram; no unrun scientific values
appear in it. Export PDF/SVG plus PNG figures and CSV plus Markdown/LaTeX tables
with provenance sidecars. Archive failures and final holdout exposure history.
Gated studies stay explicitly “not run”; never fill their table cells with
oracle or toy estimates.
