# Gated cross-agent consensus

Consensus starts as a diagnostic and a separately calibrated ablation. It is
not part of the initial K/S score and never treats majority agreement as truth.

## Eligibility and computation

For tested sender i and receiver-defined region j, remove i from all peer
selection, statistics and comparability fitting. Group peers by independently
controlled physical/security principal; multiple sensors on one RSU count as
one group and receive no extra vote. Require **at least two independent peer
groups** beyond i, all available by the same deadline, with validated coordinate
transforms, bounded source-time differences, compatible sampling/support
contexts and independently justified view comparability. Different sensors
need context normalization. A transform or nearby sensor alone cannot prove
equal visibility. If real metadata cannot justify comparison, P stays unknown.

Use the same clean-fitted count references as spatial evidence. For each
eligible group, define `z=(count-u)/b`; use one predeclared representative
sensor or a training-frozen within-group summary. Record raw counts, u/b and
group membership. No point-share ratios. For peers alone compute median m and
spread `max(z_peer)-min(z_peer)`. If spread exceeds a clean-training-fitted
comparability tolerance, mark `PEER_CONFLICT`. Tolerance fitting cannot inspect
the tested sender or outer-test outcomes. Proposed spread tolerance is the q95
of comparable clean training peer spreads. For the tested-minus-peer residual,
set epsilon to its clean training q95 and h to four times its q95-minus-q50;
require positive h and the same support/fallback rules as Phase 1. Fit these on
training leave-one-out cases only. A degenerate/unsupported tolerance or scale
requires documented fallback or unknown.

First penalty-only candidate is
`P_j=clip(max(0,z_i-m-epsilon)/h,0,1)` and `P=max_j P_j`, with epsilon and
positive h fitted only from comparable clean training differences. Freeze peer
selection, group summaries, epsilon/h and region universe before scoring i.
Unsupported regions make full P unknown while preserving partial diagnostics.
The gated ablation is `T_peer=1-max(K,S,P)` with the same structural K rule and
strict required-factor unknowns, plus its own clean threshold. It must not
borrow the K/S operating threshold.

For fixed peers, context and regions, adding points to i cannot lower P and
cannot increase T_peer. Addition below the peer upper reference can leave P
unchanged. A two-sided distance would allow filling a deficit to improve trust
and is rejected. Colluders can raise m by changing their own measurements;
show this evasion explicitly rather than claiming the single-sender property
protects against joint changes. Learned peer selection based on the tested
cloud is disallowed without a new proof/ablation.

## Required failures and synthetic scenes

| Case | Visible evidence and expected limitation |
| --- | --- |
| One attacker, two comparable independent honest peers | Show peer-only reference, tested sender count sweep and monotonicity; success is not presumed. |
| Two colluders and one honest peer | Show shifted peer statistic or conflict; honest sender may be falsely penalized. No majority-truth claim. |
| Conflicting honest peers | P unknown with spread/reason, not a fabricated consensus. |
| Missing peers / only one group | P unknown; present-but-empty peer differs from absent peer. |
| Changing membership / duplicate identities | Recompute eligible groups causally; duplicates cannot satisfy quorum; scores may lose coverage. |
| Unique honest useful viewpoint | Show how incomparable visibility prevents voting or causes a false alarm if comparability is wrong; measure honest-view loss. |
| Correlated sensors, shared weather/occlusion | Agreement can reflect common error; one security group must not be counted twice. |
| Sybil attempt | Demonstrate that strings alone cannot establish independence; evaluate assumption violation separately. |

Report quorum, comparability, missingness and conflict rates alongside the
apparent detection gain. Compare baseline and P ablation on both common support
and all attempted decisions. Unlock real consensus claims only after visible
comparability evidence and a clear statement of unverifiable assumptions.
