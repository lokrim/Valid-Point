# R01 development intake specification — 2026-10-08

**Status (2026-10-09):** R01 completed on the project-local pinned mini_7 archive; see [GR1](../artifacts/20261008T192922Z-R01/gate.md), [executed notebook](../notebooks/R01_development_intake.ipynb) and the [updated field matrix](dataset_field_matrix.md). The resource and intake text below remains the original R01 specification. No sibling data, comparison/final archive or old S prompt was used.

## Exact acquisition and resources

- Dataset `sberrio/Mixed-Signals-V2X`, revision `1a61aea747aa6bc45da2c2f085a1f1d3abc41f91`, only `train/mini_7.tar`.
- [Pinned download](https://huggingface.co/datasets/sberrio/Mixed-Signals-V2X/resolve/1a61aea747aa6bc45da2c2f085a1f1d3abc41f91/train/mini_7.tar).
- 7,894,272,000 bytes (7.894 GB; about 7.352 GiB). Published LFS SHA-256 `46e9dbe9f6e952be9186a6271abbcaaf11c965a5589d785fc278afd3eb235663`; compute locally after complete download. Metadata SHA is not local verification.
- Destination `data/mixed_signals/1a61aea747aa6bc45da2c2f085a1f1d3abc41f91/archives/train/mini_7.tar`; `.partial` beside it while downloading. Extraction under the same release root's `raw/`, only after hash/safety checks; preserve originals read-only.
- An ordinary uncompressed TAR's regular-file logical total is at most approximately archive size, so full extraction estimate is <=7.9 GB logical plus filesystem overhead. Verify TAR type, sparse members, member sizes and exact sum first. Reject links, devices, traversal, duplicate destinations and unexpected sparse expansion. Never rely on the extension alone.
- Reserve **25 GB free disk** before acquisition: ~7.9 GB archive + up to ~7.9 GB extraction + 2 GB bounded outputs/scratch + 7.2 GB margin. Avoid a second HF cache/archive copy. R01 extracts selected members only (cap 2 GB), so actual use should be lower. Stop if the inventory exceeds the cap; do not expand scope silently.
- CPU-only; target peak RSS <=4 GiB, streaming one cloud at a time. No detector/GPU dependency. Later overlays get a separate resource budget.

**Resource decision recorded:** the user performed the specified download and said to continue. Local size/hash verification passed; the user's predownload disk output and curl redirect chain were not retained. The [acquisition record](../artifacts/20261008T192922Z-R01/acquisition.json) distinguishes observed facts from those missing logs. The full work order is [R01](prompts/R01_development_intake.md).

## Bounded content inspection

1. Save pinned metadata, request/redirect URL, download size/hash, license and acquisition log. Inventory every TAR member without extracting labels or inspecting comparison archives. Inventory metadata is allowed to establish duration and stream coverage.
2. Select the earliest shared five-second interval with at least two physical agents, using filenames/timestamps only, with preference for the three vehicles plus RSU. Log missing streams. Selection cannot depend on point shapes or score outcomes.
3. Inspect first/middle/last PCD headers per available stream, plus up to 50 consecutive clouds per stream within that five-second interval (<=250 cloud bodies total). Header-only samples outside the interval are counted separately. Do not broaden duration to find favorable alignment.
4. Extract the three mini_7 odometry CSVs if present (combined selected extraction remains <=2 GB). Show exact columns, a small row sample, units supported by sources, stamp distribution, quaternion checks and finite/constant/missing value counts. Potential velocity columns are inspected, not assumed measured. Inventory label filenames only; do not load label bodies into intake or transforms.
5. Implement a small strict PCD/CSV adapter as needed, independently from cited reader semantics; no full devkit constructor or detector import. Print exact raw headers; document ASCII/binary support from observed data. Unsupported encoding blocks that stream rather than guessed parsing.
6. Validate source-time parsing, explicit sync IDs, causal odometry selection and frame composition. Show native/raw, map/top-frame plan/elevation plots with metres and shared equal axes, sensor origins, times and pose age. Check stationary surfaces across streams/time where available; mismatch remains visible. Inverse algebra alone does not validate real alignment.
7. Produce a component decision table: density feasible or blocked, motion-compensated temporal geometry feasible or blocked, cross-agent comparison diagnostic or blocked, K unavailable/conditional, intensity excluded. Record exact unavailable inputs, coverage, timing/geometry ambiguity and performance/resource measurements.

## Completion and failure

Deliver `notebooks/R01_development_intake.ipynb`, importable `io/mixed_signals.py`, intake script/config/tests, immutable run manifest, `T_R01_schema`, `T_R01_timing`, `T_R01_component_feasibility`, `F_R01_geometry`, and an updated field matrix with links. R01 succeeds technically when observations and checks are reproducible and each component has an evidence-backed disposition; it can conclude a component is infeasible. Unresolved time/frame conventions block their dependent factors, not honest documentation. Fewer than two physical agents means the intended multi-agent feasibility milestone is blocked. No scores, overlays, reference fitting, detector, comparison data or final holdout in R01. Stop after reporting the bounded gate.
