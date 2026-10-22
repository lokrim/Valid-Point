# Append-only research history

Do not rewrite or delete past entries. Append a dated correction referencing
the earlier entry when an assumption changes. Record author/action, evidence,
reason, scope and affected artifacts/gates; do not invent completed experiments.

## 2026-10-05 — H001: independent project boundary

Created Valid Point as an empty Python package and planning scaffold at the
researcher's request. No inherited code, milestones, data, installations or
scientific outputs. Read historical documents only to challenge assumptions;
see [context review](context_review.md). Reason: answer a new paper-oriented
question with explicit inference and evidence boundaries. G0 awaits review.

## 2026-10-05 — H002: release packaging and scene roles

Read official/author release documentation and public JSON metadata; verified
segment archive entries and release revision in [sources](sources.md). No raw
archive was fetched. Proposed mini_7 development; mini_10–13 comparisons;
mini_14 separate final holdout. These roles depend on metadata preflight and are
not frozen content-validated availability. Reason: require four labeled
comparison segments, avoid historical split inheritance and outcome selection.
An archive inventory does not establish labels/timing/transforms within it.

## 2026-10-05 — H003: score, GT-free and bandwidth contracts

Proposed strongest-anomaly score with strict unknowns, clean-only references,
separate 1% clean operating calibration, mandatory oracle/GT-free tracks, peer
diagnostic first, and next-frame quotas. Explicitly separated transmission from
receiver dropping and required censored-payload handling. Reason: avoid static
factor preference, GT leakage, retrospective savings and false certainty.
These are review proposals, not demonstrated findings; see [Phase 1](03_phase1_evidence.md)
and [bandwidth](05_bandwidth.md).

## 2026-10-05 — H004: evidence and stop boundary

Planned fresh-kernel notebooks and named export/test/manifests for every future
stage. All scientific acceptance items remain pending; hand calculations are
specifications. [Coverage](requirements_coverage.md) and
[setup verification](setup_verification.md) document the setup audit only.
The next action is researcher review, not executing S00 or acquiring data.

## 2026-10-05 — H005: S00 invoked and bootstrap choices

The researcher invoked S00 after the planning scaffold review, satisfying the
G0 review prerequisite for infrastructure work. S00 uses the standard library
for the importable package, with five direct bootstrap-only tools: `ipykernel`
for fresh kernels, `nbclient` to execute notebooks, `nbformat` to read/write
them, `matplotlib` to export PDF/SVG/PNG figures, and `pytest` for invariant
tests. Their resolved transitive versions and hashes are in
[requirements.lock](../requirements.lock), resolved on CPython 3.14.4/macOS
arm64 with uv 0.11.17. The initial resolver attempt could not reach PyPI from
the sandbox; resolution and install were completed with network access limited
to those bootstrap packages. No detector or research data package was added.

The first local test attempt was blocked by the sandbox's localhost socket
restriction; a test path issue was also repaired. The tests then passed with
Jupyter kernel sockets permitted. A first successful S00 run exposed a
`nbformat` missing-cell-ID warning. Stable source cell IDs and an inline
figure were added; the earlier run was retained unchanged. The final
[run manifest](../artifacts/20261005T094948Z-b2d74f78/manifest.json),
[executed notebook](../artifacts/20261005T094948Z-b2d74f78/00_bootstrap.executed.ipynb),
[test report](../artifacts/20261005T094948Z-b2d74f78/test_results.json) and
[gate](../artifacts/20261005T094948Z-b2d74f78/gate.md) record six passing tests,
fresh-kernel execution, exact config bytes, and 19 verified output hashes.
G1's infrastructure portion passed; its S01 scientific contract portion remains
pending. Research measurements/results are **not run**. The three separate
researcher choices in H003/decision notes remain open for later dependent work.

## 2026-10-05 — H006: S01 invoked; causal synthetic scene contract

The researcher invoked S01 with S00 evidence available. Added a deterministic
whole-scene NumPy generator, explicit sender/frame/deadline and transform
records, distinct parsed-empty/absent/late/malformed states, an unavailable
vehicle-kinematics fixture, independent declared security groups and a strict
canonical synthetic point-cloud reader. Evaluator object/occlusion truth is a
separate record; decision inputs keep visibility unknown. The road, wall,
moving object and three views are a constructed geometry check, not a GT-free
finding. Seed families remain the proposed development 0–9, reference 100–109,
calibration 200–209 and test 300–329; no seed role was amended or used for
fitting/evaluation.

The first [S01 run](../artifacts/20261005T102854Z-d974bbaf/gate.md) was blocked
because the sandbox denied local Jupyter sockets; it remains immutable. An
intermediate passing run exposed a legend covering the north viewpoint label,
so the figure layout was repaired and that run retained. The final
[manifest](../artifacts/20261005T103202Z-d2f4b72b/manifest.json),
[executed NB01](../artifacts/20261005T103202Z-d2f4b72b/01_synthetic_scenes.executed.ipynb),
[nine-test report](../artifacts/20261005T103202Z-d2f4b72b/test_results.json),
and [gate](../artifacts/20261005T103202Z-d2f4b72b/gate.md) support **G1 pass**
for synthetic geometry/contracts. The 25 recorded output hashes were checked
against the files. No reference fit, calibration, score, alarm, attack, quota
or real-data claim was executed. S02 remains a separate future invocation.

## 2026-10-05 — H007: S02 invoked; raw contracts pass with identifiability limits

The researcher invoked S02 after G1. Implemented only raw zero-order motion
residuals, fixed-region point counts and explicit independent availability/
eligibility. Source notebooks call the importable evidence modules. No attack
framework, external data/dependency, fitted reference, normalization, conformity
score, probability, alarm or policy was introduced. S03 was not launched.

Engineering assumptions are frozen in [raw_evidence.json](../configs/raw_evidence.json):
synthetic shared nanosecond clock, 1.5 s anchor/1.55 s deadline, motion gap
10 ms–1 s with 1 s lookback, and cloud age at most 200 ms measured at the deadline.
These are declared hand-fixture assumptions, not learned or real-sensor validity
limits. Regions are three independently receiver-defined 5 m tiles, height
[-1,1) m, frozen at t=0, with half-open boundaries and GT-free namespaces.
They are partial toy coverage; full ROI/oracle-gap work remains S04. The seed
is explicitly null: all cases are literal, deterministic inputs with no RNG,
not reference/calibration/held-out samples.

Clarified raw-versus-eligibility behavior: valid counts remain observable when
health/membership is unknown, but overall eligibility is unknown. Missing
velocity is null, never a zero residual/penalty; static motion is structurally
not applicable. Late-packet source/receipt timestamps shown for diagnosis cannot
supply causal freshness or transform-time evidence. Unsupported units/frames,
malformed fields, stale samples, invalid dt and unavailable transforms retain
explicit reasons. Region authority is separate for receiver GT-free versus
oracle evaluator namespaces; no evaluator data enters the raw GT-free demos.

Negative/limiting findings are retained: legitimate acceleration gives 0.25 m
residual, an inconsistent pose report gives 2 m, and a jointly consistent spoof
gives 0 m. Same-sender motion reports do not independently verify motion. Literal
point addition changes [2,1,0] to [3,2,0], while dense legitimate content gives
[9,0,0]. Within-region rearrangement preserves counts and removal lowers them.
Unknown visibility precludes deficit/zero-return accusations. These fixtures
establish exact computations, not detection performance, calibrated false alarms,
or any claim that a smaller/closer count is more trustworthy.

The first [passing run](../artifacts/20261005T135122Z-f8a4238c/gate.md)
(52 tests and three fresh kernels) is preserved unchanged. Post-run audit found
that an existing unanchored `!pyproject.toml` Git-ignore exception exposed the
source-snapshot copy. Anchored root documentation/packaging exceptions, added
explicit late-metadata/boolean-context validation coverage, made actual motion
conventions visible in each raw row, and added a linked evidence index. This was
a packaging/contract hardening change, not favorable-case selection. No test or
notebook execution failed. Jupyter emitted its local TCP encryption warning;
execution and tests completed successfully with local sockets permitted.

Final [gate](../artifacts/20261005T135337Z-e16df08e/gate.md), [manifest](../artifacts/20261005T135337Z-e16df08e/manifest.json),
[test report](../artifacts/20261005T135337Z-e16df08e/test_results.json) and [execution log](../artifacts/20261005T135337Z-e16df08e/execution.log)
record **53 passing tests**, three fresh-kernel notebooks and 36 visible hand
expectations. All named tables/figures, exact config/seeds, raw input JSON,
source/revision/environment and input/output hashes are in the sealed local
bundle and reports. Generated source snapshots and reports remain Git-ignored;
source notebooks contain no generated outputs. S02 raw-contract gate **PASS**;
full G2 is **blocked pending separately invoked S03 fitting/calibration/score**.
Stop here for review; none of the later prompts has been executed.

## 2026-10-05 — H008: correction to H007 final-bundle packaging verification

The post-run audit of H007's second bundle failed its assertion that all generated
files were Git-ignored. Unlike the first leak, this arose because the archived
source now included its own `.gitignore`, whose nested exceptions were active.
The raw notebook/test gates still passed; this was a failed packaging acceptance
check, not a scientific failure. H007's statement that that bundle was final and
fully ignored is superseded here. Both preliminary bundles remain unchanged.

Added an explicit `/artifacts/*/source/` ignore rule and a source-directory ignore
check in the S02 runner gate. Re-executed the same tests and all three notebooks
without changing scientific fixtures, bounds, measurements or plots. The actual
final [run gate](../artifacts/20261005T135710Z-6e4710d8/gate.md),
[manifest](../artifacts/20261005T135710Z-6e4710d8/manifest.json),
[test report](../artifacts/20261005T135710Z-6e4710d8/test_results.json) and
[execution log](../artifacts/20261005T135710Z-6e4710d8/execution.log) record
53 passing tests and three fresh-kernel notebooks. The post-run audit verified
all 80 output hashes and 31 source hashes, sequential execution counts in each
notebook, no error outputs, clean source notebooks, read-only exported files,
and no generated artifacts/reports exposed to Git. This audit passed.

The raw-contract gate remains PASS, with the consistent-spoof, legitimate
acceleration, rearrangement/removal and unknown-visibility limitations in H007.
Full G2, fitted/scored evidence and detection/probability claims remain blocked
pending separately invoked S03. No later stage was run or externally published.

## 2026-10-08 — H009: S03 clean reference and score semantics

The researcher invoked S03 after verified S02 raw contracts. Added clean-only
linear-quantile references (`u=q95`, `b=4(q95-q50)`), a specific fixed-tile/range
bin → sensor-class fallback, support of at least 200 rows across two segments,
strict unknown full-region coverage, vehicle max(K,S), preregistered static S-only,
and separate clean 1% order-statistic calibration with strict `A>c` ties. Four
parameter layers remain distinct; no factor weights or policy were fitted.

The evidence uses deterministic **illustrative clean raw fixtures**, not replayed
LiDAR or observed attack data. Reference seeds 100–109, calibration 200–209 and
test 300–329 are disjoint. The [support table](../reports/tables/T03_reference_support_S03_gt_free_illustrative_clean_fixtures_20261008T091758Z-d1642764.md)
shows zero scale in B_constant and low support in C_far_sparse, both falling
back to S:vehicle; unsupported sensor context remains unknown. The
[ablation table](../reports/tables/T03_ablations_S03_gt_free_illustrative_clean_fixtures_20261008T091758Z-d1642764.md) and
[threshold figure](../reports/figures/F03_threshold_ablation_S03_gt_free_illustrative_clean_fixtures_20261008T091758Z-d1642764.png) expose the negative result:
all 1,200 illustrative clean test decisions have A=0 and tied K/S identity.
Clean calibration chose c=0 with 0/400 alarms; this does not establish 1%
future sensor FPR or attack power. A separate all-one clean fixture chose c=1
and has zero possible alarms under strict `>`, retained as a no-power case.
The frame-level Wilson interval is displayed but lacks a clustered coverage
guarantee; per-segment calibration rates and strict hand-case unknowns are visible.

The first [S03 run](../artifacts/20261008T091106Z-2b73f795/gate.md) failed because
sandboxed Jupyter could not bind a local socket. A later passing run was
superseded after review found spatial bins shared between tiles. A subsequent pass was superseded by a figure title-layout repair. Another
[failed run](../artifacts/20261008T091349Z-79149ae5/gate.md) caught a tie-key
bookkeeping error. All were preserved. The final [gate](../artifacts/20261008T091758Z-d1642764/gate.md),
[manifest](../artifacts/20261008T091758Z-d1642764/manifest.json), [tests](../artifacts/20261008T091758Z-d1642764/test_results.json) and two
[reference](../artifacts/20261008T091758Z-d1642764/03_clean_references.executed.ipynb) /
[score](../artifacts/20261008T091758Z-d1642764/03_score_and_ablations.executed.ipynb) notebooks show 59 passing
tests, fresh execution from two kernels, 12 passing hand cases and a
nonincreasing literal point-addition sweep. G2 passes only for reproducible
semantics and leakage prevention on the illustrative inputs; empirical
operating validity and attack detection remain blocked by absent real/replayed
clean measurements. S04 and later gates were not run.

## 2026-10-08 — H010: S04 GT-free path completed; G3 negative result

The researcher invoked S04 after the S03 technical G2 pass. Added a receiver-owned
100 m × 100 m grid of 400 half-open 5 m tiles over the declared [-1,1) m height
slab, frozen at 0 ns before every tested cloud. Every tile, including empty ones,
is retained. Trusted receiver range selects context when available; the frozen
configuration explicitly uses `receiver_range:all` when it is unavailable and
never accepts sender-claimed range. Outside-ROI points are counted separately and
cannot expand or redefine the region universe. GT-free operational APIs accept no
evaluator labels, object counts, GT boxes, attack masks or clean counterparts.

The oracle-box research track is evaluator-namespaced and independently fitted and
calibrated with disjoint reference/calibration/test seeds. The optional ego-only
proposal scorer was deferred so that the first result remains attributable to
fixed tiles. Missed/extra/merged/split proposal states and association ambiguity
remain visible evaluator annotations and never affect GT-free scores. Tests prove
that withholding or reversing evaluator labels leaves GT-free decision IDs,
statuses, T values, alarms and region digests identical; sender points cannot
change region definitions; and point addition cannot improve T at fixed context.

On 12 deterministic constructed paired attempts, GT-free produced 3/7 attack
alarms versus 5/7 for oracle boxes; each track abstained once and false-alarmed on
2/5 benign cases. On the 11 common-known decisions, the attack-alarm counts were
3/6 versus 5/6, an oracle-minus-GT-free rate gap of 1/3. Fixed tiles detected a
concentrated in-ROI addition and an empty-region ghost. They missed an oracle
object split across tiles, an outside-ROI addition, and a count-preserving
within-tile rearrangement. The rearrangement retained baseline GT-free T=1 while
the oracle track alarmed. A unique honest view and changing benign content caused
false alarms. Present-empty remained a known zero without accusation; absent-cloud
was unknown and abstained. These are constructed fixtures, not empirical sensor
performance, and T remains conformity rather than an honesty probability.

The immutable [manifest](../artifacts/20261008T103246Z-cbed4e64/manifest.json),
[executed NB04](../artifacts/20261008T103246Z-cbed4e64/04_gt_free_oracle_gap.executed.ipynb),
[67-test report](../artifacts/20261008T103246Z-cbed4e64/test_results.json),
[T04_gap_cases](../reports/tables/T04_gap_cases_S04_paired_constructed_gap_cases_20261008T103246Z-cbed4e64.md),
[F04_oracle_gap](../reports/figures/F04_oracle_gap_S04_paired_constructed_gap_cases_20261008T103246Z-cbed4e64.png),
and [gate](../artifacts/20261008T103246Z-cbed4e64/gate.md) record a **technical
PASS and G3 FAIL_NEGATIVE_RESULT**. Therefore the GT-free score is not defensible
for operational readiness under the evidence available, and operational/real-policy
claims are blocked. No detector was imported, no external data was acquired, and
S05 or any later prompt was not executed. Stop for researcher review.

## 2026-10-08 — H011: authorized real-data replay replan and evidence corrections

The researcher explicitly authorized changing stage order/defaults/deferrals around actual Mixed Signals point clouds and causal temporal score trajectories. Revised canonical planning documents and added copy-ready R01–R07 prompts. No old prompt, new scientific experiment, archive download, detector install, or sibling project access was performed. Original bytes of all 29 planning documents/prompts were saved before edits in `archive/2026-10-08-pre-replan/` with SHA-256 manifest; old prompt bodies remain behind supersession banners. Existing code, tests, source notebooks, immutable runs and reports are unchanged.

Read source/modules/tests/runners/notebooks and stored manifests/gates critically. Read-only verification of 22 manifests checked 1,172 listed output hashes with zero mismatches; execution counts/errors and prior failed runs remain recorded in `audit/2026-10-08-artifact-verification.json`. Hash validity proves preservation, not research validity. See [evidence audit](evidence_audit.md) for credited computation, illustrative evidence and missing integration.

Corrections to **H009/H010, former checklist G01/G02, and former progress claims**:

- S03 residual/count rows are deterministic arithmetic rather than independently processed scene observations. Numbered scene/seed IDs do not establish independence. G2 remains a semantic fixture pass, not empirical calibration or dataset leakage assurance.
- S04 reference rows cycle literal patterns; calibration anomalies are constructed from `reference.u` or `u+1`, not clean clouds processed through the scoring path. Disjoint bundles/seeds establish bookkeeping, not independent calibration observations.
- S04's “withholding/reversing labels” test changes unused local variables, then reruns unchanged inputs. H010's claim that this proves GT-boundary isolation is retracted at that scope. Source API separation exists, but meaningful changed/withheld evaluator integration tests remain required.
- S04 does not call S02 availability checks or enforce source-time/pose/transform/context/full-reference eligibility end-to-end. A complete fixed grid alone is not full operational eligibility. Current `gt_free.decide` hard-codes vehicle K/S and receives supplied K=0 in the fixtures.
- Proposal/association failure states are annotations, not measured algorithm outputs. Tile/box count differences and the stored 3/7 versus 5/7 attack alarms, 2/5 benign alarms and abstentions are retained as constructed-case arithmetic only.
- S04's G3 failure marker is constant in code and expected by its runner/test. The negative constructed counterexamples and readiness block remain valid at that scope; this is not empirical proof that all GT-free methods fail. Technical execution passed but broader boundary/eligibility/calibration claims were incomplete.

Verified public metadata revision `1a61aea747aa6bc45da2c2f085a1f1d3abc41f91`, devkit commit `4f1f259e0d0fdc9ccfaf9f22b9627c02e263fe3d`, and ACFR commit `8b670c80e248a25924fb1e72dc649992292064db`. Direct official-site retrieval failed; indexed official pages confirmed provenance links, with freshness limitation recorded. Source inspection found documented pose/orientation/timestamps, but no consumed/verified measured velocity. The existing K residual is motion self-consistency, has no cloud input, and cannot respond to point-only edits with metadata held fixed. Pose-derived velocity is dependent and same-interval derivation is tautological. Raw RSU map coordinates, paired vehicle z offsets, legacy timestamp parsing and nearest-pose lookup require local compatibility validation; nearest future poses cannot feed causal inference. No real inputs were found in Valid Point.

Direction changes and rationale:

1. Replace synthetic-first through old S09 with R01 one-archive bounded development intake. Keep mini_7 development, mini_10–13 comparisons and mini_14 final based on unchanged public metadata, not observed performance. Labels become optional offline evaluation inputs rather than a GT-free intake prerequisite. Comparison/final outcomes remain unexposed.
2. Replace mandatory K/S and mandatory oracle tracks with minimal sensor-specific density baseline plus conditional temporal geometry and explicit candidate feasibility. Keep useful primitive computation; do not assume fixed 5 m tiles or intensity normalization transfer. No manually favorable factor weights.
3. Promote a small elapsed-time EWMA, distinct instantaneous/state/alarm records, warm-up/missing/reset/contamination behavior and memoryless comparison to the core. This supersedes H003's temporal deferral. No attack flag controls state.
4. Move deterministic real-cloud removal/displacement/count-preserving/addition overlays and bursts into development R03, then frozen grouped evaluation R05. Preserve intended/injected/realized effects, failures and companions. These are interventions on recordings, not a physical laser simulator.
5. Defer consensus, bandwidth policies/savings, detector/AP, learned combinations and broad adaptive/collusion/Sybil studies. This supersedes H003's bandwidth hypothesis and old S05/S06/S08 dependencies; it narrows the objective rather than claiming those studies succeeded.
6. New GR gates separate technical completion from scientific support. Correctly recorded infeasibility, no-power or negative results may complete a technical stage. No old failed result is erased and no favorable detection/publication result is required.

Next action is R01 only after authorization for the exact 7,894,272,000-byte mini_7 archive and 25 GB free-space reservation. No algorithm choice is requested from the researcher before feasibility. Later comparison/final acquisition has its own resource decision. Publication suitability and novelty remain unestablished with current evidence and must be assessed from completed results and related primary literature.

## 2026-10-09 — H012: planning revision completion check (Asia/Kolkata)

The H011 revision began on 2026-10-08 and completed after local midnight. Its dated snapshot/source-audit IDs remain unchanged. Final planning checks passed: all 29 original document hashes preserved, prior history retained as an exact prefix, all 11 old prompt bodies preserved behind supersession banners, seven R prompts with required sections, no broken current-document file links, and audited code/config/test/notebook bytes unchanged. Only planning files changed. See `audit/2026-10-08-planning-checks.json`. This is a planning/document-preservation check, not a scientific test or GR1 pass. Stop at the reviewable plan; R01 still requires the explicit archive/storage resource decision.

## 2026-10-09 — H013: R01 bounded mini_7 development intake

After the user completed the explicit project-local mini_7 setup and said to continue, locally reverified the archive's 7,894,272,000 bytes and published SHA-256, then inventoried all 1,788 TAR members for safe types/paths before extracting. Selected the earliest five-second interval with at least two physical agents from filenames alone; it contained all five streams/four principals. Extracted 250 consecutive selected cloud bodies (50 per stream) and all three odometry CSVs, 1,312,497,280 bytes in total, keeping the archive and selected raw files read-only. Label filenames were inventoried; bodies were not opened. No sibling, comparison or final archive was used.

Read 15 first/middle/last PCD headers and all selected bodies with a new label-independent adapter. All selected headers are ASCII XYZ+intensity and 42,598,400 XYZ rows are finite. Found 147 short-subsecond cloud names in the whole archive; legacy left-padding matches selected vehicle odometry stamps. Three 300-row CSVs have 90 columns each and variable, finite twist columns, but twist provenance/frame remain unknown. All selected vehicle cloud stamps have exact same-stamp past poses; nearest and causal lookups agree on this window, while a tested off-grid case shows nearest may use the future. Native/top-frame plan and elevation plots and sampled top/dome overlap check gross geometry without labels. Intensity is constant zero for `003` and `004`.

GR1 [technical gate](../artifacts/20261008T192922Z-R01/gate.md) passes with 84 tests and a fresh five-code-cell [executed notebook](../notebooks/R01_development_intake.ipynb). Density is feasible as an input; temporal and cross-agent geometry and kinematics are conditional; intensity is excluded. This is not a detection result. The user's curl redirect chain and predownload disk output were not retained, so the [acquisition record](../artifacts/20261008T192922Z-R01/acquisition.json) leaves them unknown. Stop at GR1; R02 and later stages were not run.

## 2026-10-09 — H014: R02 causal reader and raw-factor integration

The researcher invoked R02 after GR1. Used only the already extracted, earliest five-second `mini_7` development window (sync IDs 0–49, 50 clouds per stream), plus its three odometry CSVs. No label body, box, mask, attack schedule, clean counterpart, comparison archive or final archive entered the operational path. Added `valid_point.replay` with explicit source/arrival/deadline records, strict file allowlist/access log, latest past available pose selection, native/map-frame provenance and typed raw records; added D radial/azimuth count cells, conditional same-stream motion-compensated directed G, and a new operational wrapper. S02 arithmetic code and historical S notebooks/artifacts remain unchanged. The old S04 wrapper is documented as historical and is not used to infer eligibility.

[GR2](../artifacts/20261009T085704Z-R02/gate.md) is a **technical PASS**, separate from scientific efficacy. D is known for all 250 events with every one of 32 required cells retained. G is known for 163/250; five first-history records are unknown and 82 pairs are unknown because the bounded spatial search cannot certify a nearest distance. These are abstentions, not numeric penalties. The raw crop totals are nearly constant for several sensors (e.g. `003` 261,908–261,947 points across 50 frames), while per-cell counts and occupancy change can vary; no fitted surplus anomaly or attack sensitivity is claimed. Vehicle pose age is 0 s on this exact-stamp window. CPU measurement was 86.33 s for 250 events, wall 88.18 s, peak RSS 209,420,288 bytes. The [input](../artifacts/20261009T085704Z-R02/T_R02_inputs.md), [eligibility](../artifacts/20261009T085704Z-R02/T_R02_eligibility.md), [component](../artifacts/20261009T085704Z-R02/T_R02_components.md), [raw timeline](../artifacts/20261009T085704Z-R02/F_R02_raw_timelines.png), [alignment](../artifacts/20261009T085704Z-R02/F_R02_alignment.png), and [executed notebook](../artifacts/20261009T085704Z-R02/R02_causal_factors.executed.ipynb) show records and plots with units.

A bounded diagnostic compares top against each vehicle at four preselected sync IDs using a fixed map crop and 1 m voxels. After correcting the published top map-origin sign, 12 preselected attempts yield nine causal top–vehicle pairs with 44–77 ms source skew and potential voxel Jaccard roughly .05–.14; three first-index attempts are unknown because top had not yet arrived. This is neither visibility truth nor an X score. The first interrupted run at `artifacts/20261009T085343Z-R02/` retains raw tables and a failure note: review found vehicle D was unnecessarily tied to pose validity, and plotting hit a font-cache delay. The second run's initial test/notebook attempt was blocked by sandbox loopback socket permission; complete tests and the notebook were rerun in a fresh kernel with local socket permission. Figure/table review caught and corrected the optional X crop sign before sealing the final manifest. The [repair log](../artifacts/20261009T085704Z-R02/execution_repair.log) and [92-test report](../artifacts/20261009T085704Z-R02/test_results.xml) preserve the sequence.

The [actual isolation check](../artifacts/20261009T085704Z-R02/boundary_isolation.json) reran operational measurement with evaluator label/box/mask/schedule/clean-counterpart/outcome files inaccessible, then changed. Allowed cloud bytes, operational outputs and access logs stayed identical; a deliberate forbidden read was trapped. Tests also changed future clouds/poses and checked all earlier raw records, and exercised deadlines, stale/future/invalid poses, native frames, present empty versus absent, required-cell coverage, zero reference support, static translation and moving-object confounding. No score or temporal state exists yet, so their boundary remains an R03 obligation.

The [method/engineering freeze](../artifacts/20261009T085704Z-R02/method_freeze.json) names D-only, G-only and max(D,G) for all five streams, with strict G abstention and separate D-only coverage. G's poor `004`/`laser` availability remains visible rather than excluded after inspection. K is excluded: variable twist fields do not establish independently measured velocity/frame/online provenance; pose-derived velocity is a dependent motion diagnostic, not a point-integrity check. Intensity remains excluded. Final reference and calibration fitting wait for distinct grouped clean segments. The frozen parameters were chosen from clean physical/input feasibility and resource bounds, without intervention outcomes. `mini_7` remains one contiguous development segment, never independent scenes. Stop at GR2; R03 was not invoked.

## 2026-10-10 — H015: R03 real-cloud overlays and temporal development replay

The researcher invoked R03 after GR2. Re-inventoried the already authorized `mini_7` TAR and safely extracted 1,000 additional PCD bodies (5,267,193,300 bytes) for the first 25 acquisition seconds, capped at 300 synchronization indices. The resulting clean development replay has 1,250 PCD events, 250 per stream, and retains the three original odometry CSVs. No sibling, comparison (C0–C3), final (H), or label body was read. The archive, originals and every honest companion were hash-checked unchanged after replay.

Implemented strict float32 ASCII PCD writing/reloading, five deterministic point-overlay families, five zero-severity identity round trips, elapsed-time EWMA with per-episode/principal/sensor/arm/reference state, and distinct [raw](../artifacts/20261010T155346Z-R03/T_R03_raw_observations.md), [normalized](../artifacts/20261010T155346Z-R03/T_R03_normalized_factors.md), [instantaneous](../artifacts/20261010T155346Z-R03/T_R03_instantaneous_decisions.md), [temporal](../artifacts/20261010T155346Z-R03/T_R03_temporal_states.md) and [null-alarm](../artifacts/20261010T155346Z-R03/T_R03_alarm_decisions.md) ledgers. Executed one middle-severity sustained case per family and one displacement burst case on `003`, plus a coordinate-noise control and an in-memory calibration/timing-uncertainty control; all five streams remain in each score trace. The latter control applies 0.05 m translation, 0.2° yaw and **+10 ms modeled pose-availability delay**. The config's `source_clock_skew_ms` label is narrower in implementation: source timestamps were not changed and this does not measure actual clock error. The remaining benign grid is predeclared in the R03 config for R04 review, not executed here.

The first 10 s of real clean mini_7 records supplied **exploratory, one-segment** q50/q95 references. Of 190 sensor/context entries, 171 have positive scale and at least 50 distinct clean cloud rows; unsupported contexts remain unknown, including `004` G. A post-run check of distinct-cloud support changed no reference status. The subsequent [10,25) s clean block has fewer than 200 known observations per named sensor/arm, so both diagnostic threshold types and all alarms are null. This is neither independent-scene fitting nor empirical FPR calibration. Final >=200-row, >=2-training-segment references and separate calibration segment rules remain unchanged for R05. Clean source cadence is approximately 0.1 s; tau=1 s becomes ready for `003` D at about 3 s before the fixed 5 s onset, and g_reset=0.5 s exceeds ordinary clean gaps. Neither parameter was chosen from attack curves.

The [attempt ledger](../artifacts/20261010T155346Z-R03/T_R03_attempts.md) retains intended/injected/reader-realized fields and compact exact selected/changed/failed ID files. All 641 written development derivatives reloaded through the same production reader; no reader rejection or zero-realized file occurred in this run, and 5,785 selected rearrangement rows remained unchanged under the within-D-cell constraint. Signed development-only paired effects include D-only `003` conformity changes of differing directions and zeros across families; favorable decline was never required. [Post-offset G differences](../artifacts/20261010T155346Z-R03/T_R03_history.md) show attacked-arm geometric history can affect later records, while missing G remains unknown and no recovery is asserted. The [native/common-frame geometry](../artifacts/20261010T155346Z-R03/F_R03_geometry.png) and [timelines](../artifacts/20261010T155346Z-R03/F_R03_timelines.png) display these bounded examples with metre/second axes and evaluator intervals joined after prediction sealing.

Two development execution problems remain visible. The first [interrupted run](../artifacts/20261010T152207Z-R03/gate.md) exposed excessive G search cost; a deterministic 10,000,000 pair-evaluation guard now returns G unknown on exhaustion, without inserting a score. No clean event hit that guard. The initial rearrangement execution incorrectly moved selected rows outside all D cells while leaving their outside status unchanged. Its [invalid prediction and selection ledgers](../artifacts/20261010T155346Z-R03/protocol_deviation/reason.md) are retained; the same seed/window/severity was replayed with the declared original-cell constraint and every corrected derived PCD was reread. No outcome-based resampling occurred. A sandboxed notebook launch failed on local loopback permission; the failure was preserved and the final notebook was executed top-to-bottom in a fresh permitted kernel. Its geometry layout was inspected and repaired before sealing.

The [real-data score/state boundary check](../artifacts/20261010T155346Z-R03/boundary_isolation.json) changed and withheld evaluator labels, boxes, masks, schedules, clean counterparts and outcomes while allowed inputs remained fixed. All 180 decisions and the complete temporal checkpoint matched, with identical access logs and zero evaluator reads; a deliberately leaky control failed invariance. Actual malicious-arm prefixes, original/companion hashes, per-cell counts, selection ledgers, null alarms and exported figures pass the [technical validation](../artifacts/20261010T155346Z-R03/validation.json). A final visual/record review added the common top-frame panel and separate record exports without changing predictions; the prior manifest and gate were retained in `review_snapshot/` before resealing. The [108-test report](../artifacts/20261010T155346Z-R03/test_results_full.xml), [fresh executed notebook](../artifacts/20261010T155346Z-R03/R03_replay_temporal.executed.ipynb), [manifest](../artifacts/20261010T155346Z-R03/manifest.json) and [GR3 gate](../artifacts/20261010T155346Z-R03/gate.md) document a **technical PASS** only. mini_7 is one contiguous development scene with no calibrated alarm power or independent generalization claim. Stop at GR3; R04 and later stages were not invoked.

## 2026-10-11 — H016: R04 comparison protocol sealed without outcome exposure

The researcher invoked R04 after the [GR3 technical pass](../artifacts/20261010T155346Z-R03/gate.md). Read the current planning authority, source/method/replay/evaluation/split contracts, audit and history. No sibling project, comparison/final cloud or label body was read. The final [GR4 gate](../artifacts/20261010T211459Z-R04-0536947a1f9f/gate.md) is a **technical PASS** with no scientific outcome. Its canonical content hash is `0536947a1f9f47ef0012701c4718a5d2377753da37d658d96dfd19253810290b`; see the [freeze payload](../artifacts/20261010T211459Z-R04-0536947a1f9f/freeze_payload.json), [manifest](../artifacts/20261010T211459Z-R04-0536947a1f9f/manifest.json) and [exposure ledger](../artifacts/20261010T211459Z-R04-0536947a1f9f/exposure_ledger.json).

Kept mini_7 as development, C0–C3 as mini_10–13 and H as mini_14, without substitutions. The four comparison folds fit on two distinct clean reference segments, calibrate on a third and test on the fourth; final H fits C0–C2 and calibrates C3. [T_R04_splits](../artifacts/20261010T211459Z-R04-0536947a1f9f/T_R04_splits.md), [T_R04_parameters](../artifacts/20261010T211459Z-R04-0536947a1f9f/T_R04_parameters.md) and [T_R04_lineage](../artifacts/20261010T211459Z-R04-0536947a1f9f/T_R04_lineage.md) fix the complete sensor × arm × temporal × fold keys and the actual-reader fit/calibration requirements. Actual row IDs and thresholds do not yet exist and must be generated only during R05/R06. D-only, G-only and max(D,G), each memoryless and EWMA, are all frozen; unsupported G and no-power calibration remain reported outcomes rather than tuning triggers. The [attack grid](../artifacts/20261010T211459Z-R04-0536947a1f9f/T_R04_attack_grid.md) has 30 nonzero episodes per comparison segment plus zero controls and the declared benign grid. The +10 ms R03 timing demonstration altered modeled pose availability only; the R04 clock-skew benign stress is explicitly a future modeled alignment scenario, not a measured clock error.

The new metric fixtures exposed an initially incorrect interpretation that counted an alarm on a failed or zero-realized injection as attack detection. The final metric numerator requires reader-valid nonzero realized change and no injection failure; every scheduled attempt still remains in the all-attempt denominator. Tests hand-check eligible/realized denominators, empty support, preexisting alarm, censored delay, undefined recovery and intact grouped pairing. The final [116-test report](../artifacts/20261010T211459Z-R04-0536947a1f9f/test_results.xml) and [fresh notebook](../artifacts/20261010T211459Z-R04-0536947a1f9f/R04_protocol_freeze.executed.ipynb) passed; [split topology](../artifacts/20261010T211459Z-R04-0536947a1f9f/F_R04_split_topology.png) and [schedule](../artifacts/20261010T211459Z-R04-0536947a1f9f/F_R04_schedule.png) were visually reviewed. All 23 final run output hashes matched the manifest.

Two earlier immutable R04 attempts remain visible: [first blocked run](../artifacts/20261010T211351Z-R04-fc80d089ba48/gate.md) found a mistaken fixture assertion and sandbox loopback denial; [second blocked run](../artifacts/20261010T211405Z-R04-8f389a0e2db8/gate.md) passed focused tests but showed that the fresh notebook kernel lacked pandas. These were execution/fixture repairs before the final content hash, with no comparison exposure. A broad `pytest` invocation without `tests/` briefly collected historical artifact snapshots and failed on duplicate module names; the final scoped full project suite passed 116 tests.

Comparison/final download authorization and an actual retention budget are absent from the project record. The final exposure ledger records 20,958,199,808 free bytes at freeze versus the provisional 80,000,000,000-byte full-study reservation. This blocks R05/R06 acquisition, not GR4. The six named archive roles remain metadata only outside the already authorized mini_7. Stop at GR4; do not launch R05/R06 automatically.

## 2026-10-11 — H017: exact lineage and grouped-resample correction before handoff

After H016's successful R04 seal, a final review found that the lineage guard accepted a subset of the two declared reference segments, and the grouped summary could not consume a bootstrap draw containing two copies of the same acquisition group. The new guard requires every frozen reference segment; grouped calculations key paired variants by resample copy as well as episode/cloud ID. These are technical corrections to R04 only, made without comparison/final exposure or outcome inspection. The earlier H016 run remains immutable and is superseded by the [authoritative GR4 seal](../artifacts/20261010T211551Z-R04-80694538e854/gate.md) with content hash `80694538e8549256934b3a314301cc8ca821efe0bf36ff4071eab9681f2c039c`. Its [116-test report](../artifacts/20261010T211551Z-R04-80694538e854/test_results.xml), [fresh executed notebook](../artifacts/20261010T211551Z-R04-80694538e854/R04_protocol_freeze.executed.ipynb), [manifest](../artifacts/20261010T211551Z-R04-80694538e854/manifest.json), [split](../artifacts/20261010T211551Z-R04-80694538e854/T_R04_splits.md), [parameters](../artifacts/20261010T211551Z-R04-80694538e854/T_R04_parameters.md), [lineage](../artifacts/20261010T211551Z-R04-80694538e854/T_R04_lineage.md) and [exposure ledger](../artifacts/20261010T211551Z-R04-80694538e854/exposure_ledger.json) are the R05 inputs. All 23 output hashes matched. The resource block and scientific limits are unchanged.

## 2026-10-12 — H018: R05 prerequisite audit; comparison execution blocked (Asia/Kolkata)

The researcher invoked R05 with explicit acquisition/retention authorization as a prerequisite. Read the current index, source/method/data/replay/evaluation/notebook contracts, audit and history. Recomputed the authoritative GR4 canonical content hash `80694538e8549256934b3a314301cc8ca821efe0bf36ff4071eab9681f2c039c`; all 55 frozen source/config hashes and all 23 sealed GR4 output hashes match. No frozen file or historical artifact/notebook was changed. See the immutable [prerequisite disposition](../artifacts/20261012T121716Z-R05-prerequisites/gate.md), [verification](../artifacts/20261012T121716Z-R05-prerequisites/freeze_verification.json), [table](../artifacts/20261012T121716Z-R05-prerequisites/T_R05_prerequisites.md), [exposure ledger](../artifacts/20261012T121716Z-R05-prerequisites/exposure_ledger.json) and [manifest](../artifacts/20261012T121716Z-R05-prerequisites/manifest.json).

Preexisting C0–C3 intake manifests describe 4,996 selected clouds plus 12 odometry CSVs, totaling 26,117,294,301 extracted bytes. File presence and sizes match all 5,008 manifest entries. All four original TARs are absent at their recorded paths. Their reported archive hashes match the pins, but were not recomputed on archive bodies and cannot substitute for fresh local archive verification. No raw body, label body or H body was opened; no dataset hash/schema/frame/time validation or empirical work was performed. The circumstances/authorization of the prior acquisition and archive removal are unknown; this audit did not remove any archive. An initial shell probe used an unavailable `python` alias and was corrected to `python3`; the initial failed archive stat was followed by explicit checks of all four paths. These execution details are retained in the log.

The GR4 ledger still records absent acquisition authorization and an unset retention budget; no affirmative resource response was received during this prerequisite audit. Asked for explicit authorization. An initial question assumed local archives accompanied the intake manifests; the subsequent path check corrected that assumption and a revised question provides the exact plan. The [resource proposal](../artifacts/20261012T121716Z-R05-prerequisites/resource_plan.proposed.json) retains existing extracts, reacquires and retains the four pinned originals (31,257,047,040 bytes), and caps new run/one-active-derived-episode storage at 4,000,000,000 bytes: 35,257,047,040 additional bytes versus 37,969,920,000 free at audit. This proposal is **not authorization**. Any accepted resource amendment must be recorded before outcomes while preserving frozen method/source/config bytes.

R05 execution is **BLOCKED at prerequisites**; GR5 is **not evaluated / incomplete**, with zero comparison segments completing R05 intake validation. Required implementation, real grouped fitting/calibration, full replay grid, scientific tables/figures, tests and fresh notebooks remain pending; none are claimed by this metadata audit. No comparison predictions or evaluator outcomes exist from this run. H remains unopened by this run, and no later stage was invoked. This changes the assumption that originals are locally available, not any scientific hypothesis or frozen method.

## 2026-10-12 — H019: R05 local-data continuation and verified intake (Asia/Kolkata)

The researcher explicitly instructed reuse of the existing pinned local TARs/extracts, with no downloading, reacquisition, extraction, replacement or deletion of source data and no H access. The [new immutable-run workspace](../artifacts/20261012T134149Z-R05/execution.log) inventories mini_7 and C0–C3 metadata first; all five TARs are present and no `.tar.partial` exists. The [accepted preparation resource amendment](../artifacts/20261012T134149Z-R05/resource_amendment.json) reserves 4 GB for the run and one active regenerable derived episode. The missing-archive/resource assumption in H018 is superseded by these observed local files and the accepted amendment, not by a new acquisition.

All 55 frozen source/config hashes and 23 GR4 output hashes match. C0–C3 archive bodies were sequentially rehashed against pinned SHA-256; 5,008 extracted-file hashes and sizes were rechecked in place. Safe TAR inventory, PCD headers, stream timing, pose schema and frame inverse checks passed for all four selected segments; physical calibration and real online availability remain assumptions. No label body, mini_7 raw body or H body was opened. The [125-test report](../artifacts/20261012T134149Z-R05/test_results_permitted.xml) passed after preserving the sandbox loopback denial from the first fresh-kernel test. R05 prediction work has begun; GR5 remains pending and no evaluator outcomes have been joined. Scientific conclusions are not available from this intake.

## 2026-10-18 — H020: completed R05 prediction audit; reporting and GR5 pending (Asia/Kolkata)

The researcher reported completing the processor and requested a short inspection, plain-language explanation and notebook commands, explicitly excluding another long process. Reviewed the existing `20261012T134149Z-R05` run without running intake, prediction, report or finalization. The [review](../artifacts/20261017T190338Z-R05-review/README.md), [audit](../artifacts/20261017T190338Z-R05-review/audit.json) and [fit/calibration check](../artifacts/20261017T190338Z-R05-review/fit_calibration_checks.json) preserve current findings. All 55 frozen source/config and 23 GR4 output hashes match. All 748 scientific prediction file hashes match the original seal, all 248 episodes and 244 non-clean evaluator-ledger sets exist, and all 309,752 raw rows have complete companions, unchanged companion/pre-onset inputs and no selected original pose timestamp after its deadline. Attempt flows reconcile. Recomputed scalar references, calibration records/state and thresholds from existing saved measurements match every fold exactly; no new raw-cloud replay was performed.

The literal seal validator failed only on two mutable Finder `.DS_Store` hashes. Its reader now ignores only those non-study files, preserving every scientific hash check and the original seal. Reporting also regenerated wrong episode IDs because the stored protocol sorts mapping keys while original IDs contain an enumeration index. Reporting/finalization now recover the original pinned config order after canonical content equality checks. The 18 focused tests pass; no reporting or notebook execution was started. These changes affect new evaluation/reporting code only; frozen sources/configs remain intact.

No `T_R05_*` scientific exports, named figures, executed R05 notebooks, final manifest or GR5 gate exists yet. The run's sealed predictions are a completed computational checkpoint, not R05 acceptance or a favorable detection result. Calibration has 156/240 insufficient-support cells, 31 tagged no-power (including ten constant-zero calibrations), and 53 available cells. Preserve the interrupted resource/restart attempts and mixed implementation snapshots. The earlier clock correction note must not be read as proof that every episode used the corrected helper; the full actual raw-record inspection found no future original pose use. Historical peak storage/RSS remains unverified by this short review. Next actions are explicit `report`, then `finalize`, visual review and a GR5 disposition. H remains untouched; no later stage was invoked.
