# R01 — bounded Mixed Signals development intake

Copy-ready next execution prompt. **Not executed.**

Work only in `/Users/lokrim/Code/valid-point`, package `valid_point`. Read `planning/README.md`, `evidence_audit.md`, `sources.md`, `dataset_field_matrix.md`, `development_intake.md` and `02_data_protocol.md`. Implement and execute only R01; do not run old S prompts.

## Prerequisites and exact scope

Require explicit authorization for one 7,894,272,000-byte mini_7 download and 25 GB free disk within Valid Point. If authorization or space is absent, perform only metadata/local inventory checks, report the required resource decision, and stop without downloading. Do not search or reuse sibling projects.

Acquire only `train/mini_7.tar` from dataset `sberrio/Mixed-Signals-V2X` at revision `1a61aea747aa6bc45da2c2f085a1f1d3abc41f91` using the pinned resolve URL in `planning/development_intake.md`. Reuse a project-local copy only after verification. Expected SHA-256 is `46e9dbe9f6e952be9186a6271abbcaaf11c965a5589d785fc278afd3eb235663`. Save download size/hash/license and safe member inventory; reject traversal, links, special/sparse expansion and duplicate paths before extracting. Keep archive/raw originals immutable under the specified release root. No comparison or final archive acquisition or content inspection.

Select the earliest five-second interval with at least two physical agents from filename metadata only; include all available streams, at most 50 consecutive clouds per stream and 250 cloud bodies total. Inspect first/middle/last headers per stream and the three mini_7 odometry CSVs if present. Cap selected extraction at 2 GB and streaming RSS target at 4 GiB. Inventory labels by filename only; do not load label bodies.

## Deliverables

Create a minimal `src/valid_point/io/mixed_signals.py` adapter, `scripts/intake_segment.py`, `configs/development_intake.json`, `tests/test_mixed_signals.py`, and `notebooks/R01_development_intake.ipynb`. Follow pinned reader semantics without importing the old label-dependent explorer or installing a detector stack. Preserve raw intensity and exact timestamp strings. Show actual PCD headers, actual CSV columns/value diagnostics, source timestamps versus sync indices, missing fields and sensor-to-principal mapping.

Validate raw RSU map coordinates, top/dome translations, quaternion ordering and paired vehicle z adjustments against the cited source. Compare transforms and static geometry without labels; use latest-past odometry for causal checks and expose differences from the reference nearest-time lookup. Do not guess physical extrinsics, measured velocity, scan timing or receiver arrival telemetry.

## Meaningful tests and visible evidence

Test observed-header parsing/counts/finite values, rejected malformed headers, exact nanosecond conversion including short subsecond convention, duplicate/missing IDs, safe archive extraction, quaternion/frame composition and inverse round trips, future-pose rejection and missing velocity behavior. Show actual geometry in plan/elevation with metre axes, stream IDs, source times and pose ages; inverse algebra alone is insufficient alignment evidence.

Export `T_R01_schema`, `T_R01_timing`, `T_R01_component_feasibility` and `F_R01_geometry`. Update the field matrix with local evidence and decide feasible/blocked/conditional status for density, temporal geometry, cross-agent geometry, kinematics and intensity. Save a new immutable manifest, input/source/output hashes, exact config, tests, execution log, fresh executed notebook and GR1 gate; append history and update progress/checklist.

## Failure behavior and stopping point

Stop on hash/safety/resource failure. Document unsupported encodings, ambiguous timing, missing poses or invalid geometry and block only dependent factors; never hand-align with GT or treat absence as malice. Fewer than two physical agents blocks the multi-agent milestone. A supported infeasibility finding is a valid technical deliverable. No scoring/reference fitting, attack generation, comparison outcomes, final holdout, detector or new stage. Stop after GR1 and provide evidence for review.
