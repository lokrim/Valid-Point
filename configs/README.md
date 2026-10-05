# Configurations

`bootstrap.json` is the frozen S00 infrastructure configuration. It records
not-applicable timing/geometry fields and explicitly marks science “not run”.
Future scientific configurations require their own stage invocation and review.
Freeze and hash configurations before evaluation; never tune on outer results.

`raw_evidence.json` freezes S02 timing/units, receiver-owned region geometry and
36 literal hand cases. Seed is null and no RNG is used. The engineering bounds
are simulation assumptions, not real-sensor or fitted thresholds. Reference and
calibration lineage remain explicitly unrun.
