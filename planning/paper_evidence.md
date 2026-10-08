# Paper and demonstration evidence outline — 2026-10-08

Working topic: **What can causal, label-free consistency checks identify in perturbed real cooperative LiDAR replay?** This is a research framing, not a novelty claim or publication promise.

| Narrative / figure | Evidence needed | Claims withheld until evidence exists |
| --- | --- | --- |
| F1 Information boundary and real dataset geometry | R01 fields/transforms; R02 causal event graph; four principals/five sensors | Independent velocity, radio delay and visibility truth |
| F2 Clean reference distributions and support | Actual clean fit/calibration path, sensor contexts, all degenerate/unsupported cells | Calibrated honesty probability or guaranteed 1% future FPR |
| F3 Matched clean/attacked geometry and raw factors | R03/R05 production-reader overlays and exact realized effects | Physical laser or closed-loop realism |
| F4 Selected agent and honest-companion timelines | A/C, Z/C_time, alarms, warm-up, unknowns and evaluator-only onset/offset; frozen thresholds | Guaranteed monotonic attack decline or recovery |
| F5 Attack severity, coverage and benign false alarms | R05 full denominators and per-segment results; eligible and all-attempt rates | Broad generalization from one intersection or correlated frames |
| F6 Component and temporal ablations | Separately fitted/calibrated arms, common-support/all-attempt comparisons | Universal factor usefulness or optimal combination |
| F7 Failure gallery | Removal/occlusion equivalence, within-cell evasion, sparse/unique views, moving content, pose uncertainty, contaminated history | Robust intent attribution |
| Final check | R06 untouched mini_14 and exposure log | Replicated independent-scene validation |

Demonstration: begin with real geometry and units, play clean and attacked replay side by side with the same time axes, show agent/companion raw factors then scores, and explain one detected change and one miss/false alarm if present. If no attacks are detected, show that honestly. Evaluator annotations are visibly separate; no fabricated output fills an unavailable factor.

Paper sections: question and threat scope; dataset/release/coordinate contract; causal method and temporal state; preregistered splits/overlays/metrics; complete findings and ablations; identifiability and benign failures; reproducibility/limitations. Construction-only S02–S04 cases belong in method checks or supplementary history, never in the dataset evaluation table.

R07 must perform a current primary-literature comparison (papers and official implementations) for closely related LiDAR integrity/anomaly, cooperative geometric consistency and temporal change methods. Record what this study adds or does not add: dataset-specific evidence, causal isolation, failure analysis and reproducibility can be useful without constituting a novel algorithm. Do not assert novelty based only on the project plan. Assess venue fit, scene independence, power, threat realism and baseline fairness; recommend a report/negative-results scope when stronger claims are unsupported.

The claim ledger maps each proposed sentence to a frozen run, notebook section, figure/table, units, numerator/denominator, assumptions and limitations. Verify values and links, list not-run experiments, and keep calibration/no-power and injection failures. No AP, bandwidth-saving, probability calibration, transfer or deployment claim is licensed by this core experiment. No external submission/publication happens in R07.
