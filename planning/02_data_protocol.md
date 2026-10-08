# Dataset, time and split protocol — revision 2026-10-08

Use the pinned HF native training archives in [sources](sources.md). Preserve raw files and archive hashes; overlays go into new immutable run directories. No sibling project data or caches are authorized. Work one archive at a time, with safe member inventory and a disk preflight before extraction. No comparison/final outcomes have been inspected in this revision.

## Candidate roles and freeze

Keep mini_7 development; C0=mini_10, C1=mini_11, C2=mini_12, C3=mini_13; final H=mini_14. Published sizes/hashes still match prior metadata, so no role change is justified. Labels are optional evaluator inputs, no longer a prerequisite for GT-free feasibility. A missing label file cannot silently become an empty annotation.

Only metadata access/packaging/agent coverage/timing/calibration can justify a candidate replacement before outcomes. Record the amendment and original candidate. Unfavorable results never justify replacement. Determine acquisition adjacency from stamps/session metadata; sequential IDs are not independent scenes. If selected segments share a session, group and qualify uncertainty accordingly. At least four valid comparison segments remain the target; fewer yields an explicitly incomplete comparison study, but does not block development or a limitations report.

| Outer test | Clean calibration | Clean reference fit |
| --- | --- | --- |
| C0 | C1 | C2,C3 |
| C1 | C2 | C3,C0 |
| C2 | C3 | C0,C1 |
| C3 | C0 | C1,C2 |

Freeze method, engineering bounds, factors, contexts, temporal constants, attack grid, metrics and split hashes before running these folds. Fit each fold anew; calibrate memoryless and temporal thresholds separately on actual clean pipeline outputs from its calibration segment. Fit/calibration/test never share a scene within a fold. All sensors, windows, clean copies and interventions of a segment stay together. No random-frame split; shared raw measurements are reusable only if independent of fit parameters. Seal all fold predictions before revealing aggregate or per-fold outcomes; no sequential tuning from earlier folds.

For final H, C0–C2 supply clean references and C3 clean calibration with the original method already locked. Final H stays unopened beyond published metadata until R06 and explicit archive resource authorization. If comparison findings motivate changes, version a new study and freeze it before H exposure; disclose that comparison results became development evidence. Once H outcomes are exposed it is never restored to “untouched.”

## Source and availability clocks

Use original timestamp text plus parsed integer ns. Map to elapsed seconds only for plots. Retain synchronization index independently. The devkit legacy short-subsecond parser is checked against real names; do not silently right-pad as decimal seconds. Record timestamp gaps, duplicates, reversals, cross-stream skew and odometry sample age. Exact scan timing, deskewing and clock-error bounds remain unresolved until evidence permits a statement.

Replay events globally in acquisition order under **idealized receipt at source time**. Decision key: episode, physical principal, sensor, file/sync ID, source_ns, deadline_ns. For primary replay deadline equals event time. Tie order is deterministic by sensor/file ID; a tied event may only use already ingested events. Each scorer sees only the current event and earlier received history. Episode/run/file identifiers are opaque join keys, never features or a way to infer an intervention schedule. Missing expected events are logged by a fixed cadence/metadata schedule after its deadline, never inferred as attacks. No nearest-future pose or cloud, centered filtering, offline future-corrected trajectory or full-segment statistic enters an online decision.

Use latest past odometry with a predeclared age bound and zero-order hold as the initial causal transform assumption. R01/R02 set the bound from sample cadence and clean geometric stability, with explicit physical rationale and sensitivity, not attack detection. If poses cannot support motion compensation, retain native-frame count measurements and make affected geometry unknown. The original devkit nearest-neighbor lookup is an offline comparison only. No current evidence supports measured network delay; any later nonzero latency is an injected scenario.

## Frame and principal contract

`T_B_from_A` maps metre coordinates A→B. Validate matrices, quaternion order, handedness, inverse round trips and static landmark consistency without labels. Follow DK-frame's raw RSU map convention and paired vehicle height changes; show why the z adjustments cancel. Do not assume raw PCDs are all laser-native. The top RSU frame is the shared plotting frame. Keep raw, devkit-preprocessed body, map and top-frame arrays distinguishable with transform hashes, time/sample IDs and status.

Three vehicles and one RSU are physical principals. `top` and `dome` remain distinct sensor rows in plots but one security group. Primary agent-level view uses each vehicle's named stream and top as the RSU representative; dome is a companion sensor diagnostic, not an extra vote. Do not infer authenticated identity, sensor health or visibility from a name.

The intake matrix and failure log are authoritative for actually available fields. Geometry overlap does not establish common visibility; absent support is never a maliciousness label. Preserve raw intensity; do not pool across sensors or import detector-specific clipping as evidence normalization.
