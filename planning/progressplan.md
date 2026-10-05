# Ordered progress plan

Updated 2026-10-05. Only **P0 scaffold/planning** is prepared for review. S00–S10
are unstarted. No scientific gate is passed. Stage numbers are new Valid Point
work units, not inherited milestones.

| Stage / prompt | Dependencies | Deliverables | Principal risk | Stop/go criterion | Status |
| --- | --- | --- | --- | --- | --- |
| P0 — current setup | User brief | Empty package, directories/config, method plans, prompts, coverage and setup verification | Mistaking planning for empirical evidence | G0 review; stop before implementation | Prepared for review |
| [S00 bootstrap](prompts/00_bootstrap.md) | Researcher review of G0 | Minimal chosen environment, provenance/execution helpers, NB00 | Hidden installs/state or framework creep | Fresh notebook structural evidence, no unrequested research | Pending |
| [S01 scenes](prompts/01_synthetic_scenes.md) | S00 | Contracts, small synthetic geometry/reader, NB01 | GT leakage, empty/absent confusion | G1 causal/unknown fixtures visibly correct | Pending |
| [S02 raw evidence](prompts/02_raw_evidence.md) | S01 | Kinematics, surplus and eligibility; three NB02 notebooks | Treating self-report or zero returns as truth | Raw units, confounders/evasions/unknowns tested; no scores yet | Pending |
| [S03 references/score](prompts/03_references_score.md) | S02 | Clean fitting, calibration, weight-free score/ablations; two NB03 notebooks | Leakage, degenerate references, calibrated no-power score | G2 monotonicity and separate calibration; negative results accepted | Pending |
| [S04 GT-free](prompts/04_gt_free.md) | S03 | Fixed tiles, optional ego proposal comparison, oracle gap, NB04 | Proposal/context manipulation and low coverage | G3; failure blocks operational claim, not recording results | Pending |
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

After each invoked stage, update this table with actual artifact IDs, test and
notebook results, remaining risks and next permitted gate. Append the dated
decision/change rationale to [history](history.md) and update [checklist](checklist.md)
evidence. Never advance a stage merely because modules exist. Never auto-run the
next prompt. Failed prerequisites stop dependent work but need not erase
independent evidence.
