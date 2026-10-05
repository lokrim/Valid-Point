# Future deterministic overlays and simulation

**Plan only.** Do not implement overlays, generate attacks, or run simulations
during setup. Synthetic scenes and modules precede any real archive overlays.

## Immutable overlay contract

Each future overlay references immutable source hashes and an explicit
`overlay_id`, parent scene/segment, sender set, frame window, track, seed,
algorithm/config/software versions, units, attacker knowledge, severity,
requested target region and output paths. Derive per-frame RNG streams from
stable scene/sender/frame/attack identifiers, never process ordering or Python's
unstable hash. Save selected point IDs and transformations to replay exactly.
Never edit or replace originals; isolate derived files under an ignored run.
Include every honest companion agent and the clean matched replay.

Record three distinct fields:

1. **Intended:** requested count/position/velocity/timing change and scientific aim.
2. **Injected:** actual changes applied after constraints, serialization and quotas.
3. **Realized:** measured changes after production reading, deadline eligibility,
   transforms, region membership, score and task proxy; may be zero or unknown.

Retain failed and ineffective attempts with reasons, not just successful attacks.
No resampling until a desired effect occurs. Coverage denominators include all
scheduled attempts, feasible injections, valid derived files, eligible scores
and effective proxy perturbations, separately.

## Planned attack and benign matrix

| Mechanism | Deterministic intervention / severity | Critical control or evasion |
| --- | --- | --- |
| Graded point addition | Add 0,1,2,4,8,16,32,64 points to fixed synthetic regions; later real counts expressed also as fraction of clean region count | Oracle in-box and GT-free tile/empty-region targets; zero baseline and unchanged companions |
| Count-preserving rearrangement/replacement | Move 10%,25%,50%,100% of selected points; fixed offset/shape grid | Same global and where possible same per-tile counts; expected count-detector failure |
| Point removal | Remove 10%,25%,50%,100% deterministically | Known versus unknown visibility; empty present cloud differs from omitted message |
| Velocity spike/drift | Add configured m/s spike or m/s² drift over a causal window | Pose unchanged; compare legitimate acceleration/turns |
| Joint odometry spoof | Change pose/velocity/orientation consistently under a defined trajectory | Show self-consistency evasion and transform/context contamination |
| Dropout/delay/source-time spoof | Scheduled missing frames; delays of 0, .5, 1, 2 deadline intervals; bounded and out-of-bound timestamp shifts | Trusted receiver time unchanged; no relabeling late inputs as on-time |
| On-off / trust farming | Honest warm-up, attack bursts and quiet recovery; freeze duty cycle and onset grid | Initial score is memoryless, but quota latency/expiry has state; temporal alarms require a new controller |
| Threshold-aware | Search allowed content up to frozen score boundary, using attacker-visible refs/thresholds | Define query/compute budget and attacker knowledge; do not tune on evaluator labels unavailable to attacker |
| Collusion / Sybil | Two controlled physical groups coordinate counts/odometry; separately duplicate identities | Shared errors and false quorum; do not assume identities independent by name |
| Harmful quota packing | Select attack content first within serialized quota | Same byte cap, compare trusted selection vs untrusted sender |
| Benign faults | Noise, miscalibration, legitimate dense returns, occlusion, loss/delay and degraded sensor health | Mark as benign in evaluator; a score alarm is a false attack attribution if interpreted as maliciousness |

Severity grids are initial synthetic proposals, frozen before test seeds. Real
grids scale units transparently without selecting intensities for good detection.
Retain out-of-range/invalid interventions as failed attempts. Full compromised
fractions `{0,1/N,2/N,all}` are separate scenarios; N and independence groups are
reported. Include one attacker, two colluders, honest conflict, missing peers,
membership change and a uniquely useful honest sender.

## Simulation episodes and leakage

Start with small ordinary-Python scenes: road plane, static structures, moving
objects and several explicit sensor viewpoints with controllable occlusion.
Ground truth lives in evaluator state, never implicitly in the GT-free API.
Use 60-frame synthetic test episodes initially, clean prefix/attack/recovery
windows declared in config. Suggested seed roles: 0–9 development, 100–109
reference, 200–209 calibration, 300–329 held-out test; no family crosses roles.
Record generator version and paired seed reuse across policies. Sensitivity
sweeps are predeclared; do not claim independent samples from repeated frames.

Advance time causally, apply message scheduling and immutable overlays, read
derived files through the same reader used for clean input, compute eligible
measurements, score, next-frame quotas, then evaluate. A future full simulation
cannot read clean shadow clouds for scoring when actual payloads are partial.
On-off detection delay/recovery of a temporal alarm is deferred until its
state transitions, thresholds, initialization, reset and calibration are fixed.

## Reader and real-overlay gates

All derived point clouds must be reloaded through the **production reader**,
not a special test parser. Check fields/order/types, finite values, frame and
coordinate units, expected counts/IDs, round-trip tolerances, source/derived
SHA-256, and unchanged clean hashes. Addition/removal count effects, timestamps,
point IDs and transform effects must agree with the injected manifest; preserve
detected mismatch as a failed run. Reader rejection is not detection success.

Real overlays require validated archive hash/members, labels and association,
timestamps, transform direction and a bounded sequence preflight. One segment
is processed at a time; keep all clean/attack versions within its outer fold.
If timing or transforms are unresolved, affected real results are blocked,
while synthetic experiments may remain valid. Do not bypass the gate with
hand-aligned boxes, assumed poses, historical caches or a detector framework.
