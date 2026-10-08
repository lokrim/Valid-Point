# R02 — causal reader-to-factor integration

## Prerequisites and scope

GR1 is recorded, authorized mini_7 exists, and timing/frame/component dispositions are explicit. Read planning/03_phase1_evidence.md, temporal_spec.md and 04_consensus.md. Implement the actual operational input boundary and raw factors using only mini_7 (at most its first 30 s / 300 sync indices per stream). No interventions or comparison data. Preserve S02 arithmetic code; replace the S04 wrapper rather than assuming it enforces eligibility.

## Exact deliverables

Add `src/valid_point/replay.py` (event ingestion/causal selection), typed replay contracts, `evidence/density.py`, `evidence/temporal_geometry.py`, and the new operational wrapper; adapt availability/reader primitives only as justified. Add `configs/causal_factors.json`, `scripts/inspect_causal_factors.py`, `tests/test_replay.py`, `tests/test_causal_factors.py`, meaningful boundary tests and `notebooks/R02_causal_factors.ipynb`. Update root README/runner documentation so current R stages and historical S runners cannot be confused.

Implement D raw count cells and conditional G directed geometric novelty exactly as the method specification, with elapsed-time/pose/crop/support provenance. Report diagnostic occupancy changes. K remains excluded without usable measured velocity; derived velocity is explicitly dependent motion diagnostics. Cross-agent geometry is at most a bounded overlap/skew diagnostic and intensity remains excluded. Decide and freeze factor arms using clean availability, physical validity and resources; no favorable attacks used to choose methods. Final reference fitting waits for grouped data; do not call mini_7 independent scenes.

## Meaningful tests and visible evidence

Exercise source/arrival deadline, future/stale pose exclusion, invalid transforms, native frame handling, absent versus present empty, zero reference support and full required-cell coverage through the actual entry point. Test counts on known geometry and G on translated static geometry plus a moving-object confounder. Test no hidden future information by changing future events and comparing every prefix record.

Run operational ingestion/measurement with evaluator files (labels, boxes, masks, schedules and clean counterparts) inaccessible, then changed, with the same allowed input bytes. Assert identical operational outputs and access log, and add a deliberate forbidden-read positive control that fails the isolation check. Do not repeat S04's unused-local-variable test. Show sensor/principal mapping, selected pose/history IDs, raw factor timelines and unknowns; benchmark CPU/RSS and output coverage. Export T_R02_inputs, T_R02_eligibility, T_R02_components, F_R02_raw_timelines and F_R02_alignment.

## Failure behavior and stopping point

Time/frame failure blocks G/X; lack of sensor-origin validity blocks range-based D. A correctly scoped unavailable component is acceptable; falsely numeric evidence or boundary failure blocks scored replay. Record GR2 and proposed method arm/engineering freeze. Stop before overlays, temporal score demonstration, empirical calibration or comparison acquisition.

## Required working and evidence rules

Work only in Valid Point, package `valid_point`; do not read/copy sibling code, data or results. Read the current planning index, source/method contracts, audit and history first. Execute only this R stage. Keep historical artifacts/source notebooks unchanged; use small importable Python functions, thin scripts and new R notebooks. No detector framework, external publication or later-stage auto-run.

Operational scorer and temporal state must never receive labels, GT boxes, attack flags/schedules/masks, clean counterparts or evaluator outcomes. Use causal inputs with declared availability and strict unknowns; no honesty probability, forced attack curve or favorable-result acceptance test. Freeze predictions before evaluator joins. Preserve failed attempts and every honest companion.

Execute listed notebooks top-to-bottom in fresh kernels, show units/input geometry/raw records/unknowns/failures and actual plots. Save a new immutable run with exact config, seeds, source/environment/input/output hashes, split/reference/calibration lineage, logs, meaningful test results, executed notebooks and gate. Export named figures PDF/SVG+PNG and full tables CSV+Markdown with provenance, following planning/08_notebooks.md. Keep technical correctness separate from scientific outcomes. Append dated findings/changed assumptions to planning/history.md and update planning/progressplan.md and planning/checklist.md with actual evidence links. Stop at this stage's gate and report limitations; do not invoke the next prompt.
