# Research question, threat model, and claim contract

## Question and falsifiable hypotheses

Can an explainable, ground-truth-free sender/frame conformity score detect
specified LiDAR/message corruptions at a declared benign false-alarm budget,
and can using that score for future byte quotas improve a stated task-quality
proxy without excessive loss of honest viewpoints?

- H1: kinematic inconsistency and positive spatial surplus separate some
  predeclared corruptions from clean observations after clean-only fitting.
- H2: the GT-free track retains useful discrimination relative to oracle-box
  evidence, with measured missed cases, extra false alarms, and abstention.
- H3: at equal actual transmitted bytes, a continuous quota can yield a better
  quality/corruption/honest-view trade-off than uniform or hard gating.
- H4 (secondary): eligible peer disagreement adds useful information beyond
  K/S; it may instead add false alarms or collapse under collusion.

All can fail. Record null, adverse, ineffective-attack, and unidentifiable
results. No favorable outcome is an acceptance requirement.

## Decision and information boundary

The unit is `(segment_or_episode, sender_identity, frame_id, deadline_ns)`.
Define receiver anchor time `t_f`, deadline `d_f = t_f + delta`, and an explicit
clock mapping. Only inputs whose receiver availability time is `<= d_f` may
affect the score. Prior samples must be causal; no centered smoothing, future
pose interpolation, retrospectively corrected tracks, or future labels.
Label-derived oracle regions are a declared research exception available to
the oracle only; they never cross into GT-free scoring or allocation.

Keep these separate, with their own versioned records:

1. Raw measurements with units, availability and provenance.
2. Normalized evidence penalties and reference/support IDs.
3. Instantaneous score `T`, interval/unknown status, and reason codes.
4. Optional calibrated alarm and, only after a later gate, temporal state.
5. Next-frame byte allocation and payload admission.
6. Evaluator-only labels, attack metadata, utility and quality outcomes.

`T` is bounded conformity, not a probability of honesty, maliciousness, or
usefulness. High `T` means specified available checks found no anomaly. It does
not prove safety; low `T` can result from a benign fault. Unknown is not zero,
one, a missing numerical default, or an accusation. Useful viewpoints and
conforming senders are different quantities.

## Attacker and protected assumptions

Initially one compromised but identified sender controls its own reported
points, point fields, message content/order/omission, declared source
timestamps, and self-reported pose/velocity/orientation. It may add, remove,
rearrange, replace or compress content and exploit a known quota/threshold.
Timestamp spoofing may choose arbitrary claims; engineering age/skew limits
determine eligibility, not truth. Within-limit false timestamps remain a
tested evasion. An attacker cannot rewrite the receiver's trusted arrival
clock/log, other honest identities' packets, frozen references, receiver-owned
geometry, or the evaluator's clean original. Authentication binds a packet to
an identity; it does not certify the measurement or timestamp. Initial peer
quorum assumes independently controlled identities established outside the
score, not just distinct strings or certificates.

Later scenarios separately permit two colluders and Sybil identities. Sybil
stress explicitly violates independent-identity assumptions and cannot be
claimed solved by peer consensus. Top/dome sensors on one installation are
not two independent security principals. Receiver-clock compromise, key theft
of honest peers, or clean-reference poisoning require new threat gates.

| Case | Required interpretation |
| --- | --- |
| Graded point addition, including empty-region ghost content | Candidate surplus detection; plausible additions below reference tails may evade. |
| Count-preserving rearrangement/replacement | Expected weakness of count evidence, not silently reclassified as addition success. |
| Removal or zero returns | Cannot infer dishonesty without independently validated visibility; preserve measured zero. |
| Velocity spikes/drift | May expose inconsistent self-reports; same-sender checks are not independent motion verification. |
| Jointly consistent pose/velocity spoofing | Expected evasion unless independent geometry becomes available. |
| Dropout, delay, replay, absent messages | Availability effects, attacks only when evaluator knows injection; distinguish present empty cloud. |
| Noise, miscalibration, legitimate acceleration, occlusion, sensor failure | Benign stress strata; quantify false alarms and honest-view loss separately. |
| On-off, trust farming, threshold awareness, harmful quota packing | Adaptive stress with causal attacker knowledge and explicit controller assumptions. |
| Shared occlusion, correlated sensors, collusion, changing membership | Challenge comparability and consensus; disagreement or agreement alone proves nothing. |

## Allowed and unsupported claims

At setup there are **no research findings**. Future claims must name track,
segments, eligible/scored denominators, attack family/intensity, timing and
quota assumptions, false-alarm target, and uncertainty. A synthetic result is
about that generator. Real overlays evaluate specified interventions on a
recorded scene, not realistic closed-loop traffic behavior.

This plan cannot establish malicious intent, certified safety, calibrated
honesty probability, broad attack coverage, deployment identity security,
robustness to all removal/consistent spoofing, or generalization across cities.
Oracle-box findings do not establish deployable inference. Proxy quality is
not detector AP or fusion improvement. Receiver dropping is not transmission
saving. A GT-free failure must be a recorded negative result and blocks any
operational-readiness claim. Neural detector integration is optional later
work, never an initial prerequisite.
