# Ordered progress plan

Updated 2026-10-08. **P0 was reviewed; S00–S04 were executed.** S05–S10 remain
unstarted. G1 and the S03 G2 reproducible score/calibration-semantics gate passed on illustrative fixtures. S04 passed technical execution but **G3 failed as a negative result**, so operational readiness and real-policy claims are blocked. Stage numbers are new Valid Point
work units, not inherited milestones.

| Stage / prompt | Dependencies | Deliverables | Principal risk | Stop/go criterion | Status |
| --- | --- | --- | --- | --- | --- |
| P0 — scaffold/planning | User brief | Empty package, directories/config, method plans, prompts, coverage and setup verification | Mistaking planning for empirical evidence | G0 review; stop before implementation | Reviewed by S00 invocation; no empirical claim |
| [S00 bootstrap](prompts/00_bootstrap.md) | Researcher review of G0 | Minimal chosen environment, provenance/execution helpers, NB00 | Local Jupyter kernel needs localhost sockets; installed dependency lock is CPython 3.14/macOS arm64 resolved | Fresh notebook structural evidence, no unrequested research | **G1 infrastructure passed**: [run gate](../artifacts/20261005T094948Z-b2d74f78/gate.md), [manifest](../artifacts/20261005T094948Z-b2d74f78/manifest.json); six tests passed. Science not run. |
| [S01 scenes](prompts/01_synthetic_scenes.md) | S00 | Contracts, small synthetic geometry/reader, NB01 | GT leakage, empty/absent confusion; synthetic visibility is evaluator-only | G1 causal/unknown fixtures visibly correct | **G1 passed**: [gate](../artifacts/20261005T103202Z-d2f4b72b/gate.md), [manifest](../artifacts/20261005T103202Z-d2f4b72b/manifest.json), [executed NB01](../artifacts/20261005T103202Z-d2f4b72b/01_synthetic_scenes.executed.ipynb); nine tests. No score or GT-free result. |
| [S02 raw evidence](prompts/02_raw_evidence.md) | S01 G1 passed | Kinematics, fixed-region counts and independent eligibility; three NB02 notebooks | Consistent spoof has zero residual; acceleration is nonzero; removal/rearrangement evade counts; visibility unknown | Raw units, confounders/evasions/unknowns tested; no scores yet | **Raw-contract PASS**: [gate](../artifacts/20261005T135710Z-6e4710d8/gate.md), [manifest](../artifacts/20261005T135710Z-6e4710d8/manifest.json), [tests](../artifacts/20261005T135710Z-6e4710d8/test_results.json); 53 tests, three fresh kernels and 36 hand checks. Full G2 remains blocked pending uninvoked S03. |
| [S03 references/score](prompts/03_references_score.md) | S02 | Clean fitting, calibration, weight-free score/ablations; two NB03 notebooks | All 1,200 test scores tie at A=0 on deterministic fixtures; no empirical sensor FPR/power; frame clustering | G2 monotonicity, lineage, separate calibration; negative results accepted | **G2 semantic PASS**: [gate](../artifacts/20261008T091758Z-d1642764/gate.md), [manifest](../artifacts/20261008T091758Z-d1642764/manifest.json), [tests](../artifacts/20261008T091758Z-d1642764/test_results.json), [reference notebook](../artifacts/20261008T091758Z-d1642764/03_clean_references.executed.ipynb), [score notebook](../artifacts/20261008T091758Z-d1642764/03_score_and_ablations.executed.ipynb). 59 tests, two fresh kernels, 12 hand cases. Threshold c=0 with 0/400 clean calibration alarms; a separate c=1 no-power fixture is recorded. No empirical detection claim. |
| [S04 GT-free](prompts/04_gt_free.md) | S03 | Fixed tiles, optional ego proposal comparison, oracle gap, NB04 | 3/7 GT-free attack alarms versus 5/7 oracle on all attempts; 2/5 benign false alarms in both; constructed-only evidence | G3; failure blocks operational claim, not recording results | **Technical PASS; G3 FAIL negative result**: [gate](../artifacts/20261008T103246Z-cbed4e64/gate.md), [manifest](../artifacts/20261008T103246Z-cbed4e64/manifest.json), [67 tests](../artifacts/20261008T103246Z-cbed4e64/test_results.json), [NB04](../artifacts/20261008T103246Z-cbed4e64/04_gt_free_oracle_gap.executed.ipynb), [T04](../reports/tables/T04_gap_cases_S04_paired_constructed_gap_cases_20261008T103246Z-cbed4e64.md), [F04](../reports/figures/F04_oracle_gap_S04_paired_constructed_gap_cases_20261008T103246Z-cbed4e64.png). Optional proposal scorer deferred; failure annotations retained. Operational/real-policy claims blocked. |
| [S05 consensus](prompts/05_consensus.md) | S04 | Leave-one-out diagnostic and gated ablation, NB05 | Correlated peers/collusion/unique honest view | G4 or documented unknown consensus; baseline can continue | Pending |
| [S06 byte policies](prompts/06_bandwidth.md) | S04; S05 disposition recorded | Serialization, causal quotas, proxies, NB06 | Retrospective savings, hidden full clouds, harmful packing | G5 exact ledgers/equal actual-byte controls | Pending |
| [S07 overlays](prompts/07_overlays.md) | S02, S04, S06 | Immutable seeded overlay registry/round trips, NB07 | Source mutation, silently failed attacks | G6 full intended/injected/realized ledger | Pending |
| [S08 synthetic evaluation](prompts/08_synthetic_evaluation.md) | S03–S07 and consensus disposition | Preregistered sweeps, metrics, uncertainty, NB08 | Cherry-picking, abstention inflation, proxy overclaim | G7 complete case inventory; hypothesis may fail | Pending |
| [S09 real data](prompts/09_real_data.md) | S08, resource decision, frozen protocol | One-archive intake; four outer folds; final H gate; three NB09 templates | Fewer than four labels, invalid geometry, leakage, scene correlation | G8/G9; do not replace scenes based on results | Pending |
| [S10 paper](prompts/10_paper.md) | S08 and explicit S09 completion/blocked disposition | Paper exports, claim ledger, reproducibility bundle, NB10 | Turning toy/oracle results into operational claims | G10; scope paper to evidence actually obtained | Pending |

NB identifiers expand to exact filenames and named outputs in
[notebook acceptance](08_notebooks.md). The [checklist](checklist.md) lists proof
requirements, not just code paths. If S09 is incomplete, S10 can prepare a
synthetic-only negative/limitations report; it cannot declare the requested
real comparison complete. Optional temporal/learned/detector/probability/
transfer stages require new prompts, notebooks and gates before work begins.

S04 is complete and stops for review. Its [run gate](../artifacts/20261008T103246Z-cbed4e64/gate.md)
records a technical pass and explicit G3 failure. Receiver-owned 400-tile geometry,
GT isolation, independent track fitting/calibration and monotonic point addition
passed, but the constructed comparison exposed misses, false alarms, an abstention
and the count-preserving blind spot. S05 was not launched. Because G3 failed,
dependent operational/real-policy claims remain blocked unless the researcher
reviews and separately amends scope; no data acquisition or external publication occurred.

After each invoked stage, update this table with actual artifact IDs, test and
notebook results, remaining risks and next permitted gate. Append the dated
decision/change rationale to [history](history.md) and update [checklist](checklist.md)
evidence. Never advance a stage merely because modules exist. Never auto-run the
next prompt. Failed prerequisites stop dependent work but need not erase
independent evidence.
