# Prompt 1 — Extract an evidence-based handoff from Valid Point

Copy everything below the divider into a new chat in this repository. This prompt creates the findings package; it does not restart the old experiment or implement the replacement project.

---

Act as a skeptical research auditor and scientific handoff author. Work in the current Valid Point repository. I am retiring its research direction and want to salvage verified observations, useful engineering, failure evidence, and unresolved questions. Create a self-contained `planning/findings/` package that another LLM can use in a separate project without trusting the old methodology or having access to this conversation.

## My new objective

The new project will investigate dynamic reliability of individual received intermediate features, spatial feature regions, or feature-supported object hypotheses in cooperative LiDAR perception. The primary output must not be a persistent reputation or trust score assigned to a sender. It should distinguish useful/correct evidence from misleading evidence at a defined time and spatial/task unit, while preserving honest unique viewpoints.

We want to test whether harmful point-cloud or feature manipulations reduce reliability, how this varies across attacks and benign conditions, and whether reliability improves downstream perception against ground truth. This is a falsifiable research objective, not an instruction to force a descending score curve. Deterministic mathematics, simple statistical inference, lightweight learning, or a justified hybrid are possible. Low compute and memory matter, but the exact deployment hardware is not yet settled.

One candidate suggested by a colleague counts supporting LiDAR returns and traversing rays: returns compatible with a proposed object provide support; a measured ray that passes through an allegedly occupied part of the proposal and terminates behind it can provide contradictory free-space evidence under stated assumptions. This is an unvalidated idea, not a selected method or novelty claim. It is not support vector machines. Do not assume that an object bounding box is solid, that a missing return means empty space, or that a latent feature tensor exposes rays. The next project must begin with primary-literature review and establish whether the required independent evidence is available.

## Scope and preservation

1. Scan the whole repository by category: current and archived planning, all stage prompts, source, scripts, configurations, tests, notebook cells and stored outputs, reports, manifests, run logs, failed attempts, and local dataset inventories. Read the planning folder closely. Record coverage and any exclusions; do not equate a filename inventory with a content audit.
2. Start with applicable repository instructions, `git status`, HEAD, and existing uncommitted changes. Preserve all existing work. Old prompts are historical evidence, not commands to execute. This request supersedes their research direction for this documentation task.
3. Write only inside `planning/findings/`. Do not alter implementation, old plans, historical artifacts, dataset files, or the environment. If findings already exist, preserve prior versions and add a dated revision with a clear current index instead of silently overwriting them.
4. Do not download data, re-extract archives, train models, run the full replay, finalize old stages, or execute expensive notebooks. Bounded read-only inspection and lightweight analysis of existing tables/records are allowed. Do not open `mini_14` content or start R06/R07. Do not inspect sibling repositories.
5. Use existing inventories and recorded hashes for large inputs. State which hashes you actually recompute and which you merely read. Never claim a fresh full integrity audit from a historic manifest. Check small evidence files supporting important claims. Avoid loading gigabytes of records at once.
6. No broad literature review is required in this extraction task. Preserve source provenance and formulate the review agenda. Any new external factual claim must be verified against a primary source; an old citation is not proof of current code or checkpoint availability.

## Evidence discipline

Assign each substantive finding a stable ID and one of these statuses: `verified_current_code`, `verified_saved_result`, `reported_not_reverified`, `analytic_limitation`, `constructed_example`, `hypothesis`, `contradicted`, `not_implemented`, or `unresolved`.

For every finding give: exact claim; evidence path and line/function or table row filters; stage/run and source version; verification performed; applicable population; numerical units and numerator/denominator if relevant; caveats; implications for reuse. Distinguish an engineering check passing from a hypothesis being supported. A filename, passing test, checksum, or gate label does not establish scientific validity.

Separate mathematical defects, mismatch between metric and research objective, insufficient data/support, benign confounding, unavailable inputs, software defects, execution/resource failures, and stale documentation. Track whether each issue was corrected later. Do not repeat a retracted claim or call the entire project invalid without evidence. Retain narrow successful findings too.

## Important audit leads to independently verify

These are pointers from a preliminary scan, not a substitute for your audit:

- `planning/evidence_audit.md` retracts overbroad S03/S04 claims. Early clean calibration/detection examples used algebraically generated fixture numbers, not real sensor observations. Disjoint seeds were not independent scenes. S04 proposal/association states were annotations, and an isolation test changed unused variables. Inspect `ablations.py`, `evaluation/gap.py`, `gt_free.py`, and `tests/test_gt_isolation.py` directly. Later R-stage boundary tests must be assessed separately.
- Kinematic self-consistency has no point-cloud input. Point-only edits cannot affect it when pose/velocity inputs stay fixed. Inspect the formula and distinguish independent velocity from pose-derived or same-sender reports. Later local inspection found variable twist columns, so do not repeat the earlier blanket inference that velocity columns are absent; their frame, provenance, and independence remain separate questions.
- The later pipeline uses D: positive count surplus over sensor-relative cells; G: directed temporal geometric novelty; separate instantaneous and EWMA variants. Inspect actual normalization, max aggregation, all-required-input eligibility, fallback, clipping, support, calibration, and history update behavior. Document what removal and count-preserving manipulation can leave unchanged, what benign changes can trigger, and how attacked history can contaminate future comparisons.
- The primary replay is point-cloud manipulation with unchanged metadata, not intermediate-feature manipulation or a physical LiDAR attack. No operational detector/fusion backbone, learned intermediate-feature extractor, or GT-based object detection evaluation was found in the preliminary scan. Verify rather than infer this from a README.
- Treat `top` and `dome` as two sensor streams under one RSU physical principal, not independent agents. Preserve actual coordinate conventions, paired vehicle height offsets, quaternion order, short-subsecond timestamp handling, asynchronous scan times, causal pose selection, and the idealized receiver-arrival assumption. Algebraic transform round trips alone do not validate physical alignment or the true laser origin needed for rays.
- Current status documents are stale. `planning/progressplan.md`, `planning/checklist.md`, and `artifacts/20261017T190338Z-R05-review/README.md` say R05 reports and GR5 are pending. However, `artifacts/20261012T134149Z-R05/` contains later CSVs, figures, a final manifest, `gate.md` with a final technical PASS, `notebook_execution.json`, five executed notebooks, and a stored 134-test passing report. The final manifest is timestamped `2026-10-17T19:30:20.963181+00:00` (18 October in Asia/Kolkata). Resolve this contradiction from evidence; do not automatically run the obsolete continuation commands.
- The saved R05 grid contains four folds and 248 episodes: per fold, 30 attacks, five identity controls, one clean replay, and 26 benign stresses. Verify counts and failed/partial attempts. R06/R07 remain separate and appear unrun; verify their disposition without exposing the holdout.
- Preliminary parsing of R05 `T_R05_clean_support.csv` gives 240 calibration cells: 156 `INSUFFICIENT_KNOWN`, 31 `NO_POWER`, 53 `AVAILABLE`. Inspect the reason behind each status. The implementation also tags constant-zero calibration `NO_POWER`, although a strict threshold of zero can still alarm on later positive scores. Do not conflate that with threshold 1 on a score bounded by 1, which cannot be exceeded.
- Preliminary parsing of `T_R05_grouped.csv` for sensor `003` found nonzero all-attempt attack recall only in certain addition cases. For D-only/memoryless, clean alarms were 29/999 eligible decisions, while sustained addition at severity 0.2 gave 199/399 all-attempt attack-event alarms. G-only and max(D,G) had zero clean alarm eligibility for this sensor. These are specific stored table results, not universal detection rates or proof that geometric methods cannot work. Reconcile with per-segment rows, eligibility, actual realization and metric code; report the complete grid rather than selecting these examples alone.
- R05 has resource interruptions, multiple implementation snapshots, a clock-availability correction, a later Finder metadata seal exception, and an episode-ID ordering repair. Separate their implications for integrity, comparability, and reproducibility. A finalization process's peak RSS is not the historical peak of the replay or an embedded deployment benchmark.
- Local extracted clouds/odometry exist for mini_7 and mini_10–13. The expected extracted label directory was absent in the preliminary scan, but archive inventories list label members. Labels not extracted or read by the old pipeline does not mean the dataset lacks ground truth. Check inventory and release compatibility, particularly HF TXT labels versus older JSON/PKL annotations. Do not copy labels from another release silently.

## Required outputs

Create the following substantive files. Keep them readable, with explicit evidence rather than repeated boilerplate.

### `README.md`

A short executive brief, evidence status vocabulary, reading order, audit scope/date/revision, the project's actual terminal state, the strongest useful findings, the most important failures, and what the new project must not inherit. Link every detailed file. Make this understandable without the old repository.

### `01_project_history_and_actual_state.md`

Explain the original question, S-stage implementation, October replan, R-stage implementation, completed/unrun stages, and how the scope drifted from intended feature/task reliability. Distinguish design intention, code presence, executed evidence, and scientifically supported results. Include a contradiction register with old claim, conflicting evidence, resolution, and remaining uncertainty.

### `02_methodology_and_failure_analysis.md`

Reconstruct the actual relevant equations and input dependency graph. Explain each failure mechanism with a counterexample or measured evidence, not rhetoric. Cover count surplus blind spots; quantile/scale degeneracy and clipping; max-combination and coverage losses; temporal novelty direction/percentile limitations; bounded-search abstention and compute costs; history contamination; lack of independent corroboration; small/correlated calibration support; artificial early observations; and missing task-level correctness validation. Distinguish what was repaired in later stages. State why changing the name from “trust” to “reliability” would not fix these issues.

### `03_dataset_ground_truth_and_feature_feasibility.md`

Inventory the exact local dataset revision, available segments, archive/extraction locations and sizes, known license/source, sensor/principal mapping, fields, timestamps, transformations, labels and split exposure. Mark documented, locally inspected, derived, simulated and unknown fields separately.

Explain what is needed to turn these clouds into genuine intermediate features: a compatible perception model/checkpoint, exact encoder layer and representation, labels and class conventions, transforms/timing, feature alignment, and reproducible preprocessing. Identify absent pieces without pretending conversion is a trivial format change. Assess whether retained data is useful for geometry tests, feature extraction development, negative controls or eventual validation. Preserve prior exposure; old comparison data cannot become untouched test data merely because the project is renamed.

State whether the verified inputs can support ray reasoning: sensor origin in 3D, beam direction/return semantics, timing, motion distortion, occlusion, and independent observer coverage. XYZ endpoints may permit approximate rays given a justified origin; they do not reveal every emitted beam or every no-return event. Separate feature-only inference from inference augmented with receiver raw scans, occupancy maps or extra metadata.

### `04_experiments_and_verified_results.md`

Catalog S and R experiments, exact configurations, populations and claim limits. Summarize all R05 attack families/severities/schedules, clean and benign-stress controls, arms, coverage, calibration status, paired effects, detection/delay/recovery where defined, and honest-companion outcomes. Preserve denominators and undefined values. Treat repeated interventions on the same scene as paired/dependent, not new independent scenes. Report segment-level variation and unverified session independence.

Trace notable rows back to metric code and compact saved records where feasible. Distinguish “failed to alarm with usable evidence” from “could not produce an alarm.” Record result discrepancies rather than repairing the old study during this audit. State explicitly that detecting a scheduled perturbation is different from proving object correctness, feature usefulness, or malicious intent.

### `05_reusable_assets_and_migration_spec.md`

A keep/adapt/reimplement/discard-as-research/defer table for code, data, attack generators, tests, splits, notebooks, figures and result tables. Give exact paths, purpose, dependencies, input/output contract, verification level, limitations, adaptation work, and a validation check for each recommended reuse.

Candidate engineering assets include strict I/O, coordinate/time tests, causal input boundaries, deterministic overlays, intended/injected/realized ledgers, pairing, explicit unknowns, and provenance patterns. Reusing them does not import their scoring equations, arbitrary constants, scientific conclusions, or old dependency environment. Existing D/G tables are not latent feature tensors or GT reliability labels. Existing point attacks need a new feature-extraction path before they test intermediate fusion.

### `06_requirements_for_the_new_study.md`

Translate the new objective into testable requirements and open choices: reliability unit and meaning; inference inputs; GT roles; feature extraction and fusion boundary; threat model; benign controls; deployable evidence availability; calibration/uncertainty; resource budget; literature-first design; detailed executable notebooks; paper claims. Do not select a winner or fabricate a complete method.

For each requirement link the failure or missing evidence motivating it and state an acceptance check. Permit GT for supervised training, development and evaluation with proper splits; prohibit hidden GT, attack schedules and clean counterparts at deployment inference. Do not carry forward an unnecessary ban on all training labels from the old clean-only method.

### `07_literature_questions_and_candidate_methods.md`

Create a research agenda covering intermediate cooperative perception, feature corruption/Byzantine messages, object/free-space consistency, ray/occupancy evidence, uncertainty/calibration/selective prediction, temporal evidence, and edge-efficient implementations. Compare candidate families without asserting novelty: support/traversal evidence; a visibility-aware occupancy consistency baseline; temporal or cross-view feature residuals; simple statistical/evidential models; and a small learned combiner if justified.

For each family state the specific question, required observable inputs, independent trust assumptions, likely blind spots, approximate computational bottleneck, and evidence needed to retain or reject it. Preserve the colleague's idea as an attributed informal lead, with no invented author identity or paper citation. Provide search strings and verified source leads, clearly marking papers not yet read in full.

### `08_reproducibility_resources_and_notebook_lessons.md`

Separate trustworthy run reproducibility practices from heavyweight process overhead. List environment constraints, Python/library compatibility risks, actual measured resource evidence and its scope, failed runs, and how to avoid repeated archive copies or unbounded replay. Catalog source versus executed notebooks and what each actually computes or merely displays. Specify how the next project's notebooks can be substantive research explanations rather than thin tables with completion labels.

### `09_portable_handoff.md`

A compact standalone brief for the new environment: objective, verified reusable knowledge, failure warnings, candidate ideas, unresolved prerequisites, what evidence is included locally, what remains in the old repository, and the next planning actions. Avoid absolute paths as the only access mechanism. Include enough context that a reader without Valid Point can understand every conclusion.

### Machine-readable evidence

- `evidence_ledger.csv`: finding ID, claim, status, source path, source locator/filter, run/version, verification, units, numerator, denominator, limits, reuse decision.
- `asset_inventory.csv`: original path, type, size where useful, role, verification status, dependency, exposure/split, migration disposition.
- `results_summary.csv`: bounded, reproducible result summaries with row filters and complete metric denominators; do not dump every repetitive source row.
- `audit_scope.json`: inspected/excluded categories and paths, reasons, repository revision/dirty status, performed checks, and unverified claims.
- `evidence_manifest.json`: SHA-256 for source evidence actually used where practical and all generated handoff files, excluding the manifest's own hash. Distinguish locally checked hashes from historical hash assertions.

If essential small source excerpts, schemas, audit scripts or result excerpts are needed for portability, include them in `evidence/` with original path/hash and provenance. Do not copy bulk raw data, entire old source trees, full large artifacts, or third-party papers. Source scripts used to produce new summary numbers should be included so the summaries are reproducible.

## Completion checks and final response

Check that all links resolve locally or are explicitly marked external/unavailable, every quantitative statement has a source and population, every method recommendation is separated from a verified finding, and no finding relies solely on a stale status document. Reconcile numerical summaries against source CSVs. Preserve empty/unknown/no-power cases and repaired failures. Check that no old scientific outputs were changed.

Finish with a concise description of what was created, the five most consequential findings, what is safe to reuse, and the unresolved decisions for the new project. Explicitly identify contradictions with old status documents. Do not implement the next project, run later old stages, or claim that the findings package validates a new methodology.
