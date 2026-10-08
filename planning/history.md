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
