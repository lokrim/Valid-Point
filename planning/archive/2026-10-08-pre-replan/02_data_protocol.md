# Dataset packaging, roles, time, frames, and splits

## Verified boundary and acquisition plan

The [dated source check](sources.md) verifies an author-maintained release with
segment TARs, including `mini_7` and `mini_10`. Individual PCD frame downloads
are **not** an advertised unit. Choose an archive, acquire it in a later
authorized intake, then inspect selected frames locally. No data is present
or assumed in this project. Do not reuse a sibling project's paths or caches.

Process one archive/sequence at a time. Budget disk for archive plus extraction,
bounded overlay work, manifests and compact measurements; do not assume archive
bytes equal peak disk usage. Validate safe archive members (no traversal or
external symlinks), hash the archive, inventory all members and label coverage,
extract to an immutable raw directory, and process bounded chunks. Preserve
source hashes/URLs/revision and compact clean measurements between sequences.
Later deletion of scratch copies must not delete originals needed for audit;
record a reproducible reacquisition route and retention decision.

## Proposed roles, chosen before outcomes

Use availability, public-label status and metadata quality only. The following
candidate manifest is based on the verified inventory, not performance or
historical splits. It becomes frozen after metadata-only preflight; it is not
a claim that contents have been validated.

| Role | Candidate | Constraint |
| --- | --- | --- |
| Development only | `mini_7` | Reader, units, transforms, plots; never counts among comparisons or fits frozen real evaluation references. |
| Comparison C0 | `mini_10` | Distinct labeled segment, outer held out once |
| Comparison C1 | `mini_11` | Distinct labeled segment, outer held out once |
| Comparison C2 | `mini_12` | Distinct labeled segment, outer held out once |
| Comparison C3 | `mini_13` | Distinct labeled segment, outer held out once |
| Untouched final H | `mini_14` | Available additional archive: reserve now, inspect only access/packaging metadata until final protocol lock. |

Public competition train membership provides candidates for a new research
split; it does not imply all frames have labels or make the official unlabeled
validation/test archives usable as labeled comparisons. Metadata preflight must
record frame counts, actual label availability, agent coverage, duration,
timing, transform sources, sensor groups and acquisition adjacency. Missing
label files differ from valid empty annotations. Never impute absent labels as
zero objects. Consecutive segment IDs may be correlated; verify session/time
metadata and report it, without promising scene diversity from names alone.

If a candidate fails access/label/transform checks, record the failure before
outcome inspection. A replacement requires a dated metadata-only protocol
amendment and a new freeze. Once outcomes have been observed, do not replace
unfavorable or missing selected segments; label the planned study incomplete.
Fewer than four valid distinct labeled comparison segments means no completed
real-data validation or policy comparison. Synthetic work can still proceed.

## Frozen outer evaluation with minimum four comparisons

| Outer test | Clean calibration only | Clean reference fitting only |
| --- | --- | --- |
| C0 | C1 | C2, C3 |
| C1 | C2 | C3, C0 |
| C2 | C3 | C0, C1 |
| C3 | C0 | C1, C2 |

The method, context bins, fallbacks, target FPR, attacks, severity grid, budget
grid and plotting/metric definitions are locked before any outer results.
For each fold, fit normal ranges on clean reference segments; choose the
operating threshold only on that fold's clean calibration segment. Attacked
variants cannot fit references or calibrate benign thresholds. The simple
baseline has no learned factor weights. Any later learned/adaptive model must
use segment-grouped inner fitting/tuning confined to reference segments; if
there are too few groups for defensible tuning, disable that extension. Do not
use another fold's test outcomes to revise this fold. Execute all frozen folds
before revealing their outcome summary.

All agents, frames, clean counterparts, overlaps, attack variants and episode
windows of a segment stay together in each fold. Synthetic train/calibration/
test scene seeds also remain disjoint. No random frame split. Group references
are recomputed per fold; globally fitted caches are prohibited. Cross-fold
clean measurement reuse is allowed only if independent of fitted parameters.
Persist split hashes and assert disjoint provenance before each run.

For final H, predeclare C0–C2 as clean reference/training and C3 as clean
calibration, with method/policy choices already locked. Open H once for final
evaluation; reserve other available segments untouched if expanding. An
outcome-driven revision retires that holdout's untouched status and requires
an explicitly new study. Report every segment and aggregate, including failed
segments. Four outer groups give wide generalization uncertainty, even if there
are many frames. Adjacent segments from one intersection do not establish
independence or cross-dataset transfer.

## Time and coordinate contracts

Keep integer nanoseconds for source timestamp, receiver arrival, anchor,
deadline and odometry times; retain original strings and conversion provenance.
Do not infer identical acquisition times from a synchronization index. Match
within declared tolerances, never by floating-point equality or nearest future
sample. Source age and receiver transport delay are separate fields.
The archive has no verified packet-arrival telemetry: initial replay assumes
arrival equals mapped acquisition time plus a declared synthetic latency.
Name this idealized assumption in every real timeline; delay/drop results use
injected schedules, not measured network claims.

Represent `T_receiver_from_sensor(t)` as a homogeneous rigid transform with
explicit source/target frame, units, handedness, quaternion ordering, extrinsic
and odometry provenance, and validity interval. Proposed receiver is the top
RSU frame; sender clouds remain native until an authoritative composition is
validated. Verify pose frame versus LiDAR mounting frame, static RSU relations,
rotation orthogonality, inverse round trips, and known geometric landmarks.
Do not estimate unknown extrinsics from attacked clouds or GT agreement.
Causal pose propagation is allowed only with a separately bounded age/error
contract; future interpolation is prohibited at inference. Offline reference
GT may be used for evaluator sanity checks, not hidden online correction.

Engineering skew, age, pose-gap, finite-value and transform limits are explicit
configuration values with units and a source/rationale, set before evaluation.
Missing calibration, unsupported time mapping, unverified coordinate convention
or excessive extrapolation produces unknown affected evidence. Cross-agent
comparison additionally needs verified comparable views; a valid transform is
necessary but insufficient. Real overlays require all archive, timestamp,
label and transform gates for a bounded sequence first.
