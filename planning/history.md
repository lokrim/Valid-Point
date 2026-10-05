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
