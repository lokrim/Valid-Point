# Phase 2: quotas, exact bytes, payloads and task value

## Timing and enforcement

A full cloud received at frame f can inform `T_f`, which controls quota
`q_(f+1)` only after score computation and control-message delivery fit the
declared scheduling deadline. It cannot save the bytes already used at f.
If computation finishes too late, use the last eligible score or unknown.
Record score age and quota effective frame. Propose one-frame score expiry as
the initial synthetic default; late/absent updates become unknown, never
silently carry high trust indefinitely.

At cold start, use the explicit unknown policy. Under quotas, the receiver sees
only delivered points: truncated counts cannot be treated as full-cloud counts
or evidence of improved trust. Mark S unknown for a partial cloud unless a
separately justified sampling-aware reference exists. The first closed-loop
simulation therefore reserves predeclared uniform full-cloud audit rounds
(proposed every 5 frames); their bytes count against the same multi-frame
budget and must fit a frame budget or be deferred visibly. Compare no-audit and
audit schedules and report availability/utility trade-offs. No hidden clean/full
cloud may feed a live policy. An ideal full-observation policy is a separately
labeled hindsight diagnostic only. Online reference refitting is disabled to
avoid quota-driven censoring and trust-farming contamination.

Primary transmission experiment assumes a trusted link scheduler or relay
enforces per-identity quotas before the constrained hop, and accounts for all
traffic on that hop. A malicious endpoint cannot force excess transmitted
bytes there, but may choose malicious contents within its quota. If only the
receiver drops packets, count upstream transmitted bytes in full and claim
only admitted/processed savings. Saturation, attempted excess, enforcement
location, control latency and ignored identities belong in the model.

## Byte ledger and payload units

Initial proposed wire format: one 64-byte fixed header per emitted frame/sender
packet plus fixed 16-byte point records (four little-endian float32 fields:
x,y,z,intensity). Validate this with actual serialization later; schema version
and identity/timestamp fields must fit the frozen header or its size must be
amended before experiments. Record control/audit metadata costs explicitly.
No compression initially. File/PCD size is not a wire cost. If fragmentation,
transport headers, authentication tags or compression are added, count actual
encoded bytes and rerun comparisons; do not claim modeled application bytes
equal radio airtime.

For each sender/frame record:

- **Attempted:** bytes the sender offers, including blocked excess and relevant
  control traffic; also record the full-cloud demand separately.
- **Transmitted:** actual serialized bytes crossing the modeled constrained hop.
- **Admitted:** valid bytes accepted by receiver after schema/quota checks.
- **Processed:** admitted byte-equivalent payload entering score/task processing
  (plus separately measured compute time); no conflation with bytes read twice.
- **Fused:** bytes whose points actually contribute to the declared aggregate
  or proxy; a proxy aggregate is not a detector/fusion result.

Track rejected/malformed/control bytes separately so accounting reconciles.
Header-only/empty messages cost bytes; absent packets cost none. Use integer
capacities and exact serialization to test `sum(transmitted)<=budget`.

## Equal-budget policies

Use the same active identity set, offered data, payload selector, frame horizon,
audit schedule and effective total byte budget B for all policies. Subtract
common control and emitted-header costs first. Convert remaining capacity to
integer point slots; allocate by deterministic largest remainder, cap by sender
demand, and redistribute only among eligible recipients. Tie order rotates by
a frozen seed to avoid systematic sender preference. If B cannot fund all
headers, a deterministic rotating subset gets packets; show starvation.

| Policy | Relative weight for known score T | Unknown rule |
| --- | --- | --- |
| Uniform | 1 | Same membership share |
| Hard gate | 1 if T>=tau, else 0 | Explicit unknown reserve; unknown is not a failing threshold |
| Linear proportional | T | Explicit unknown reserve |
| Smooth continuous | `epsilon + (1-epsilon)*T*T`, proposed epsilon=.05 | Explicit unknown reserve |
| Unknown-score policy ablation | Known senders follow the selected base rule | Compare reserve, uniform treatment, and quarantine; measure honest exclusion and abuse |

Default unknown reserve: each unknown sender gets half of its uniform point
slot entitlement; distribute the remainder to known senders by policy weights.
If all are unknown, use uniform allocation. If known hard-gate weights all
vanish, leave that remainder unused; do not secretly admit failed senders.
Proposed reserve=.5 and epsilon=.05 are policy parameters, not factor weights
or score semantics. Freeze via synthetic development, show sensitivity, and
keep the same settings across outer tests. Deliberate dropout can exploit the
reserve; quantify it. Distinguish structural K inapplicability from unknown T.

Include an absolute-quota ablation `q_i=T_i * uniform_quota_i` to test the
phrase “trust .4 means 40% bandwidth.” It may leave unused bytes; the primary
linear policy is proportional normalized allocation. Neither interpretation
is a property of T. Forty percent bytes does not imply forty percent utility
or sixty percent attack-impact removal.

Hard gates and demand caps can under-use B. Report both common-budget-cap
results and strict equal-**actual**-byte comparisons, matching transmitted point
slots/overhead over the same horizon. Downsample higher-use arms deterministically
to common feasible byte totals and rerun the proxy; do not interpolate fabricated
results or use padding as useful payload. Report infeasible comparisons as such.

## Selection and adversarial packing

Start with deterministic seeded uniform point selection without replacement
on an honest sender's serialized records. A second receiver-owned spatially
balanced selector may use frozen tiles; neither uses GT boxes. Include a
malicious ordering/content case where the sender fills its allowance with the
most harmful points. Selection guarantees require a trusted selection point:
an untrusted sender need not obey requested random sampling. Report both
trusted-relay selection and adversarial-packing assumptions, including any
extra upstream traffic to that relay. Seed knowledge available to an attacker
is declared; no claim of secret randomness unless enforced.

## Usefulness and proxy outcomes

Synthetic evaluator knows occupied task cells and clean scene geometry. Freeze
an evaluation grid independent of scoring tiles. Report separately: true-cell
coverage (unique true occupied cells hit / true cells), false occupied-cell
fraction, geometric displacement error for matched structures, admitted attack
point influence, and honest unique-view loss relative to a clean full-payload
reference. Do not hide these in an arbitrary favorable scalar. A required
single proxy objective for a hindsight upper bound is lexicographic: maximize
true-cell coverage, then minimize false occupied cells, under the same bytes;
label this evaluator-only and unattainable online.

Leave-one-agent-out **PROXY** utility is the change in these outcomes when one
agent is removed with all other decisions held fixed; a second explicit
reallocation experiment may change the budget distribution. Hindsight oracle
**POLICY** upper bound selects payloads with knowledge of clean truth and
attacks under identical wire constraints, using exact finite search on small
synthetic cases or a proven relaxation bound. A heuristic must be called a
hindsight comparator, never a certified upper bound.

Real-data policy comparisons must use GT-free scores/proposals and measured
byte ledgers. GT may evaluate label-associated support/coverage proxies, with
annotation incompleteness caveats, but these are not AP. Genuine detector AP,
detector-based utility or fusion gain require the later independent gate.
