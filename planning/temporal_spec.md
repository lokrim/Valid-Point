# Core causal temporal experiment — revision 2026-10-08

Temporal behavior is required alongside memoryless scores; it is no longer a later optional extension. Use one small exponentially weighted anomaly state per `(episode, principal, sensor, method_arm, reference_version)`. No history crosses episodes, clean/attacked replay arms, agents or fold/reference versions. Same-principal multiple sensors do not share state automatically.

## Records and equation

Keep `RawEvidence`, `NormalizedFactors`, `InstantaneousDecision(A,C)`, `TemporalState(Z,C_time)`, and `AlarmDecision` distinct with time, source IDs, validity and reasons. `C_time=1-Z` is smoothed conformity, never an honesty probability.

For an eligible event at time t with known A in [0,1], let Δt be actual elapsed seconds since the previous eligible update within a contiguous valid run and `rho=exp(-Δt/tau)`. Then

`Z_t = rho * Z_prev + (1-rho) * A_t`.

Initialize at the first eligible event with `Z=A`; expose it as **warm-up**, not a confident initial score/alarm. Warm-up requires both >=10 eligible updates and >=3*tau seconds of contiguous valid support. Raw A/C and Z remain visible during warm-up; operating temporal alarm is null until ready. The memoryless arm has no accumulation warm-up but requires its factor's own valid history (G needs a previous cloud). Include common post-warm-up comparisons and each arm's full coverage separately.

This is an event-update EWMA using real elapsed time, not an integral of unavailable evidence or a decay triggered by attack truth. Dense sampling with constant A and the same endpoints must agree with sparse valid sampling within tolerance. Equal-time duplicate events are rejected/no update; time reversal invalidates that event without mutating state. Do not use frame index or synchronization k as time.

## Missing, stale and recovery behavior

- Missing/invalid required factors: no update; retain last numeric Z internally with its age and mark current public C_time/alarm **unknown**. Do not decay to good or bad during silence.
- Never bridge a long unknown gap with a large EWMA weight. If time since last eligible update exceeds `g_reset`, discard state and restart warm-up on next eligible A. Initial candidate g_reset=.5 s, determined from clean source cadence, distinct from modeled transport delay. If Δt<=g_reset, a resumed eligible sample updates with actual Δt; missingness and gap are still logged.
- A known sample above/below Z can raise/lower state; sustained anomalies accumulate and clean-like subsequent evidence can reduce it. No forced monotonic attack decline or automatic recovery at evaluator offset. Missing periods cannot qualify as recovered.
- Alarm is `Z>c_temporal` with strict ties and separately clean-calibrated threshold; instantaneous alarm uses `A>c_instant`. Primary model has no extra alarm latch/hysteresis. Persistence is measured from threshold crossings; adding a latch would need a new state/threshold protocol.
- End episode: seal state and reset. Reference/config changes start a new episode/version, never continue with inconsistent scale.

## Parameter choice, contamination and tests

Initial `tau=1 s`; predeclared development sensitivity {.25,1,2} s. Choose and freeze the primary tau using mini_7 clean sampling coverage and whether a >=3*tau warm-up plus declared attack/recovery windows fit the sequence. Use 1 s when feasible; otherwise choose the smallest listed value meeting those constraints and record why. Do not select tau to maximize attack curves. Report the sensitivity arms only if fully frozen before comparisons, each separately calibrated. Engineering gap bound and minimum updates use clean cadence/availability, not attack schedule or final data. A too-short recording yields insufficient temporal evidence rather than invented persistence.

Final references/calibration use separate segments per [data protocol](02_data_protocol.md). Development internal time blocks may illustrate behavior but are not independent-scene calibration and cannot certify FPR. Clean calibration must run with the same initialization, missingness, geometric history policy and warm-up; calibrating A then reusing its threshold for Z is prohibited.

References remain frozen. EWMA memory is O(1) per stream/arm, but G holds one prior voxel cloud and pose. Neither score nor history can read evaluator clean copies. An attacker can contaminate G's recent geometry, persist until adaptation, exploit warm-up or force abstention. Freezing scalar reference ranges prevents online reference poisoning, not these history risks. Plot alarm coverage and resets so disappearance of alarms during missingness/warm-up is not called recovery.

Meaningful tests: analytically known constant/step sequences with irregular times; time-unit conversion; boundedness; first-sample/warm-up; equal-time duplicate and reversal; hold on missing; reset on long gap; short-gap resume; no cross-agent/arm state; checkpoint-resume equivalence; prefix invariance to future-event changes; no schedule/label access. Assert recurrence and eligibility, never a desired attack curve. A deliberately injected forbidden evaluator read must make the boundary test fail.
