# Valid Point: real-cloud replay research plan

Revised **2026-10-08** under the researcher's authorized planning revision. This is the current planning authority for package `valid_point`. No dataset archive, new experiment, detector, or old stage prompt was run during revision. Start with [the plain-language overview](overview.md), [evidence audit](evidence_audit.md), and [next executable prompt R01](prompts/R01_development_intake.md).

The experiment replays real Mixed Signals observations, modifies one agent's clouds in separate deterministic copies, and compares causal conformity trajectories against matched clean replay. Favorable detection and publication are hypotheses, never gates.

| Canonical document | Responsibility |
| --- | --- |
| [01 Research contract](01_research_contract.md) | Question, hypotheses, threat model, information boundary and claims |
| [02 Data protocol](02_data_protocol.md) | Frames, time, agent identity, splits and holdout protection |
| [Field feasibility](dataset_field_matrix.md) / [source verification](sources.md) | Exact documented fields, provenance, unknowns and pinned sources |
| [Development intake](development_intake.md) | One archive, resource decision, bounded inspection and feasibility gate |
| [03 Method](03_phase1_evidence.md) / [temporal specification](temporal_spec.md) | Minimal candidates, fitting, instantaneous and temporal records |
| [04 Cross-agent evidence](04_consensus.md) / [05 bandwidth disposition](05_bandwidth.md) | Conditional geometry and explicit deferrals |
| [06 Replay and attacks](06_attack_simulation.md) / [07 Evaluation](07_validation.md) | Deterministic overlays, episode grid, metrics and denominators |
| [08 Evidence delivery](08_notebooks.md) / [paper outline](paper_evidence.md) | Visible notebooks, figures, claims and reproducibility |
| [09 Gates and risks](09_decisions_and_gates.md) | Technical acceptance, failure behavior and genuine decisions |
| [Progress](progressplan.md), [checklist](checklist.md), [coverage](requirements_coverage.md) | Current execution status and proof requirements |
| [Prompts](prompts/README.md) | R01–R07, individually invoked implementation work orders |
| [History](history.md) / [audit](evidence_audit.md) | Append-only decisions and corrections to prior claims |

S00–S04 remain historical work. Old S00–S10 prompts are marked superseded; do not execute them as the current sequence. Their original bytes and the previous canonical documents are retained in [the dated snapshot](archive/2026-10-08-pre-replan/snapshot_manifest.json). Existing artifacts, notebooks, code and tests remain unchanged. Historical setup/context documents describe their original date, not today's readiness. If an old README or runner conflicts with this plan, this plan governs future work; R02 will update executable entry-point documentation.
