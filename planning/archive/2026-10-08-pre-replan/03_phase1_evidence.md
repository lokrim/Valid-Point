# Phase 1: evidence, tracks, score, fitting, calibration

This is a proposed mathematical contract, not implemented research. Defaults
are reviewed/frozen before use; all numeric examples are hand calculations.

## Schemas and separation

| Record | Minimum fields |
| --- | --- |
| DecisionInput | segment/episode, sender/security-group, sensor type, frame, anchor/deadline/arrival/source time, message state, cloud hash/fields, causal odometry samples, transform ID/validity, receiver context ID, track, region IDs |
| RawEvidence | key, factor/region, value or null, units, status (`known`, `unknown`, `not_applicable`, `invalid`), reasons, availability time, source IDs; retain partial observations separately |
| ReferenceBundle | fit segment/seed IDs, context map and support, quantile method, u/b values with units, fallback lineage, engineering spec ID, software/config hash |
| NormalizedEvidence | K/S/P or null, reference ID, context/support count, factor eligibility, raw row links, reason codes |
| ScoreRecord | T or null, lower/upper conformity bounds, required/observed factor set, strongest factor/region, track, version, reference ID, reasons; no utility or binary truth label |
| CalibrationBundle | calibration segments, alpha, threshold/tie rule, support, achieved clean rate/uncertainty, fitted score version; separate from reference fitting |
| EvaluatorRecord | clean/benign/attack identity, intended/injected/realized effects, labels, proxy outcomes; never a scorer input in the GT-free track |

Availability fields: `present_nonempty`, `present_empty`, `absent`, `late`,
`malformed`. A parsed empty cloud can yield raw count 0, while an absent cloud
yields null. Neither is positive evidence of dishonesty. An eligible empty
cloud with frozen regions can have known S=0 for surplus only; visibility and
removal detection remain unknown. A vehicle missing kinematics never receives
K=0. Structural inapplicability is predeclared by sensor role (e.g. static RSU),
not selected dynamically to improve a sender's score.

## Factor contracts

| Factor / raw units | Inputs available by deadline; independent information | May detect | Benign confounders and evasions | Exact unknown conditions |
| --- | --- | --- | --- | --- |
| Vehicle kinematic self-consistency: displacement residual m; supporting dt s, speed m/s, acceleration m/s² | Two causal positions, prior reported velocity and orientation with known conventions. Same-sender inputs are not independent verification; receiver timing is independent. An external motion observation would be a new factor. | Inconsistent velocity spike/drift or pose jump | Real turns/acceleration, delayed odometry, integration error; jointly spoofed pose/velocity can pass | Missing/nonfinite pose/velocity/orientation, nonpositive/out-of-range dt, unsupported frame/unit conversion, future/late/stale samples, no supported clean reference; static sensor is not_applicable |
| Positive spatial point surplus: count points per fixed region; context range m, volume m³, sensor class | Present valid cloud, frozen receiver-defined region and transform; clean expected-count reference. Region/normalization must not be defined by the tested sender's current points or claimed range | High-density addition in covered tiles/boxes | Dense real traffic, reflectivity, range changes, proposal errors; plausible injection, rearrangement and removal may evade | Absent/late/malformed cloud, invalid transform, no region in declared coverage, unavailable independent context, unsupported reference/fallback. Visibility unknown forbids deficit inference but does not erase a valid positive count |
| Leave-one-sender-out disagreement: context-normalized residual, dimensionless; raw peer counts retained | At least two independent eligible peer groups, common region/time and validated comparability, clean per-sensor references, tested sender excluded | An unusually high sender against agreeing comparable peers | Unique honest view, occlusion, correlated faults, two colluders; shared anomalies or below-consensus addition can evade | Insufficient quorum, dependent identities, unmatched region, timing/transform mismatch, missing context/reference, conflicting peers, unverified visibility/comparability |
| Freshness/missingness/transform/sensor health: ns/s, booleans, invalid-point fraction | Trusted receipt clock/log, membership schedule, parser/finite checks and sourced calibration validity; sender health reports are untrusted annotations | Staleness, absent/invalid evidence; not intent | Network loss, planned absence, sensor fault; attacker can force abstention | Missing trusted clock/membership or unverifiable health claim => unknown corresponding eligibility; never impute nominal health |

No agent fraction of total group points enters trust. Count deficit, absence
of peer support and zero points are not dishonesty evidence without independently
known visibility. Engineering-invalid reports are excluded with reasons, not
silently converted into attack positives or high conformity.

## Two required tracks

**Oracle-box research:** GT boxes define fixed regions to isolate factor
behavior. Use evaluator association and oracle geometry only in explicitly
oracle-namespaced inputs. This can study in-box surplus; missing annotations,
new ghosts outside boxes and box-association errors limit coverage. It never
licenses a claim of deployed score availability.

**Ground-truth-free:** start with a receiver-owned fixed grid of 5 m × 5 m
horizontal tiles over a declared 100 m × 100 m receiver ROI with a separately
declared height slab. These are proposed synthetic engineering defaults, not
dataset coverage assertions. Freeze all tile IDs, including empty tiles,
before examining a sender. Count only finite transformed points within this
ROI; track outside-ROI points separately. Context uses sensor class, tile
geometry, and range from an independently validated receiver-side pose when
available. If range relies solely on spoofable odometry, omit that range bin
and use a broader fixed context or abstain. Attacker-driven reference switches
must not reward injection.

A later lightweight proposal ablation may cluster ego-only geometry available
by the deadline. Freeze proposals before reading other senders; do not require
a detector. False proposals can create false surplus, missed proposals can
hide attacks, split/merged objects distort counts, empty ego regions may contain
valuable unique sender observations, and changing content shifts distributions.
Fixed tiles do not require object association; GT object association is
evaluator-only. Proposal association, if used, must be ego-only causal geometry
with an ambiguity state; unmatched/ambiguous regions stay visible and cannot
be discarded to improve metrics. Show maps for all such failures.

GT-free score and Phase 2 policy APIs cannot accept labels, GT boxes, attack
masks, clean counterparts or evaluator utility. The evaluator can use GT for
outcomes, stratification by object count, and oracle-gap analysis, after decisions
are frozen. Tests must prove perturbing/withholding GT cannot change GT-free
scores/quotas. Do not condition GT-free reference bins on GT object count.

## Raw formulas and clean references

For a vehicle with causal samples `t0 < t1 <= deadline`, use the first simple
zero-order velocity predictor:

`r_K = || (p1 - p0) - R0 v0 (t1 - t0) ||_2` metres.

The orientation/velocity convention and causal age bound must be verified.
Normalizing for interval and sensor context accounts for finite integration
error; this tests self-consistency only. Later integration variants are ablations.

For each frozen region j: `r_S,j = count(points inside region j)` points.
Fit contextual clean upper reference `u = q95(r)` and scale
`b = 4 * (q95(r) - q50(r))` from clean training only. Quantile convention is
frozen (linear empirical quantiles). Define `a(r;u,b) = clip((r-u)/b,0,1)`.
The factor penalties are `K=a(r_K)` and `S=max_j a(r_S,j)`. This is a proposed
scale, not a universal physical bound; evaluate its sensitivity on development
only, then freeze. Multiple regions increase the chance of a high S, so
calibrate the combined sender/frame score, not a per-region false-alarm claim.

Initial context hierarchy: sensor class × fixed receiver tile/range bin
(spatial), sensor class × dt bin (kinematic), then sensor-class-only, then
documented pooled context only where units/semantics are comparable. A fit
context needs at least 200 clean rows drawn across at least two training
segments (synthetic: two independent scene seeds). Low support or zero b uses
the predeclared broader context; if none is supported, return unknown. Do not
choose a positive arbitrary scale to hide a degenerate reference. Show support,
fallback frequency, temporal correlation and range uncertainty. Reference
changes always generate a new bundle and invalidate old calibration.

The sender score uses a fixed region universe. If any required region has
unknown reference/transform, full spatial coverage is unknown; retain the
maximum of measured penalties only as partial diagnostic evidence. A smaller
known subset cannot masquerade as a complete high S/T assessment.

## Weight-free combiner and strict unknowns

For vehicles, required factors are K and S; for preregistered static sensors,
only S is required. Peer P is excluded from the first baseline.

```text
required = {K,S} for vehicle else {S} for known-static sensor
if every required factor is known:
    A = max(required penalties)
    T = 1 - A
    interval = [T,T]; status = known
else:
    T = null; status = unknown
    A_observed = max(known required penalties, default=0)
    interval = [0, 1-A_observed]  # diagnostic bounds, not a replacement score
return raw links, reference IDs, reasons, strongest known factor/region
```

No manually fixed factor weights such as 40/30/30. The strongest eligible
anomaly determines the score; its identity can change each frame. Saturation,
ties and missing factors remain visible. For fixed regions/context/reference,
adding suspicious points cannot decrease S or increase T. Pure within-tile
rearrangement can leave T unchanged. Adding data cannot improve eligibility
through data-dependent proposal selection. Simultaneous odometry/context
spoofing is a separate stress case, not covered by the fixed-context proof.

| Hand-worked input (not results) | Expected output / explanation |
| --- | --- |
| K=.2, S=.7 | T=.3, strongest=S |
| K=.8, S=.1 | T=.2, strongest=K; no fixed factor preference |
| K unknown, S=.2 on vehicle | T=null, interval=[0,.8], `KINEMATICS_MISSING` |
| Static sensor, S=.2 | T=.8, K=`NOT_APPLICABLE_STATIC` |
| Present empty cloud, valid regions/references, K=.1 | S=0, T=.9; removal/visibility remain unknown, no claim of honesty |
| Absent cloud, K=.1 | S unknown, T=null, interval=[0,.9], `CLOUD_ABSENT` |
| Count 10→14, u=10,b=8, K=.2 | S 0→.5; T .8→.5; injected points do not improve conformity |
| Count unchanged after rearrangement | S unchanged; record blind spot |
| No regions or unsupported context | S unknown, `NO_REGION` or `REFERENCE_UNSUPPORTED` |

Reason vocabulary also includes `LATE`, `FUTURE_SAMPLE`, `CLOCK_UNVERIFIED`,
`TRANSFORM_INVALID`, `SENSOR_HEALTH_UNKNOWN`, `VISIBILITY_UNKNOWN`,
`PEER_QUORUM`, `PEER_CONFLICT`, `VIEW_INCOMPARABLE`, `SURPLUS_HIGH`,
`KINEMATIC_RESIDUAL_HIGH`, `REFERENCE_FALLBACK`, `SCORE_PARTIAL`.
Reasons describe measurements/eligibility, never inferred criminal intent.

## Four parameter layers and operating calibration

1. Engineering validity limits: time skew/age, finite coordinates, pose gap,
   transform tolerance, ROI and required factor roles. Set from documented
   contracts or declared simulation assumptions, not held-out success.
2. Clean-fitted ranges: u/b, contextual support and frozen fallback hierarchy.
3. Clean calibration: propose benign false-alarm target alpha=1% of known-score
   sender/frames, with additional all-decision and per-sender reporting. On
   separate clean calibration observations, set `c` to the empirical order
   statistic at `ceil((n+1)*(1-alpha))`, clamped to threshold 1 if beyond n.
   Alarm iff `A>c` (equivalently T<1-c); ties do not alarm. Fewer than 200 known
   calibration rows => operating calibration unavailable. A c=1 with no power
   is retained as a negative result, not retuned on attacks. Clustered frames
   invalidate IID coverage guarantees; report achieved rates and grouped
   uncertainty, never promise exactly 1% on future scenes. Unknowns abstain;
   report abstention beside FPR to prevent apparent success by abstaining.
4. Policy parameters: quota shape, exploration reserve, stale-score age and
   payload rules; specify/freeze separately under the byte protocol.

Do not merge benign stress faults into clean fitting silently. Report clean
and benign-stress false alarms separately; a future benign-mixture calibration
is a separately named experiment. Calibration failure or insufficient support
blocks calibrated detection claims but permits diagnostic plots.

Component ablations: K-only, S-only, max(K,S), oracle versus tiles/proposals,
contextual versus broad references, strict unknown coverage, and gated P.
Compare on common eligible cases and all intended decisions including unknowns.
Later adaptive/learned combiners require training-only parameter fitting,
monotonicity constraints under point addition, separate clean calibration and
identical outer splits/budgets. Fitted weights are never universally optimal.
Probability calibration, reliability diagrams or ECE need a new binary target
and held-out probability model; they do not apply directly to T.
