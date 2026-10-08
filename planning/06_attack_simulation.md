# Replay and deterministic interventions — revision 2026-10-08

This is open-loop **recorded point-cloud replay with deterministic overlays**, not a physical laser compromise simulator or closed-loop traffic experiment. Clouds are immutable originals; each derived arm has its own reader inputs and causal history. All agents are replayed in event-time order under the explicit ideal-arrival model. Honest companions and matched clean runs are retained; identical companions need not have identical scores if an optional peer-dependent method is later added.

## Small initial grid

Primary compromised principal `003` (metadata fallback in the research contract); no receiver compromise. Select it before scores. No point intervention changes poses, timestamps, identities or honest companion bytes. Attacker generator may inspect its own current unmodified scan and its previous local scans, as a compromised sender could; the **scorer** may not access those clean counterparts. Primary target selection uses this sender's available geometry only. GT-box/object-targeted interventions, if later added, are evaluator-assisted diagnostics in a separate table and never pooled with operational-target attacks.

| Family | Initial severity grid and exact intended operation | Required realized checks / likely limitation |
| --- | --- | --- |
| Random removal | Remove floor(f*N) uniformly selected rows without replacement, f={.1,.3,.6}; N=current sender cloud count | Exact removed count, retained fields/order and spatial distribution; count surplus generally cannot detect it |
| Localized removal | Freeze one target region after the first 3 s clean prefix from sender-observable geometry: choose the most occupied valid D cell aggregated over that prefix, deterministic ID tie-break. Remove fraction {.25,.5,1} of rows in that fixed cell | Region selection IDs/time, local and global removed fractions, zero-target cases; unknown visibility prevents intent attribution |
| Displacement | Select 25% of rows by seeded IDs; add local +x offsets {.2,1,3} m in validated sensor-relative coordinates, preserving other fields | Exact count equality, vector/norm in m, crop/cell crossings. Ordinary displacement already preserves total count. |
| Count-preserving rearrangement | Stronger count evasion: move 25% of rows by attempted {.2,1,3} m seeded horizontal offsets, constrained to remain in each row's original frozen D cell | Preserve total **and per-D-cell** counts. Fixed bounded proposal budget of 10 directions per point; no valid offset => unchanged row and recorded failed move. Report actual moved fraction/norm distribution; no resampling until score changes. |
| Addition | Add floor(f*N) points, f={.01,.05,.2}, uniformly in a 2 m-side cube centered at the centroid of the sender's target cell during first 3 s; freeze center before onset | Added and reread counts, in/out crop fractions, density and realized geometry. Intensity copied by seeded sampling from current sender intensities, explicitly synthetic, never an intensity detection claim. N=0 or no center => zero/failed injection retained. |

For every family include a zero-severity identity overlay control; retain original filenames/metadata convention in isolated derived roots. Algorithm/seed, coordinate frame, rounding, constraints and serialized precision are frozen before held-out execution. One primary seed `20261008`; derive per-point/frame random streams via a documented SHA-256 key of segment/principal/file/family/severity/replicate, not traversal order or Python hash. A second seed may be a predeclared sensitivity, not another independent scene.

Use first 25 seconds relative to earliest multi-agent sequence time (cap 300 sync indices; stream timestamps remain independent). Two schedules, half-open in acquisition seconds: sustained [5,15), bursts [5,7) and [10,12). Prefix permits state warm-up; remainder measures recovery. If the sequence is too short or a stream absent, keep that attempted cell with a reason and any observed partial episode; do not move onset to a favorable region. Same schedules and rows across methods. R03 demonstrates one middle-severity sustained case per family and one burst example on mini_7; R05 runs the entire frozen family×severity×schedule grid (30 nonzero episodes per segment, plus clean/identity controls). Do not materialize every archive copy simultaneously.

## Overlay and event ledger

Each attempted episode has base hashes, split/fold, principal/sensor, threat version, attacker knowledge, interval, seed key, targets, algorithm/config/source versions, and intended severity. Per affected cloud retain:

1. **Intended:** requested selection, counts/fraction, displacement and frame, time interval and diagnostic aim.
2. **Injected:** actual selected/added/removed/moved row IDs, assigned attributes, bytes written, failed constraints and serialization differences.
3. **Realized after production read:** accepted/rejected status, finite/count checks, actual point/cell changes, displacement distributions, in/out crop fraction, eligibility, coverage and score effect joined only offline.

Reload every derived file with the **same production PCD reader and frame adapter** as its clean counterpart. Read→write→read identity controls establish precision tolerance. Rejected files/failed injections remain attempts, never detection successes. Check original and honest companion hashes before/after; retain selection/manifests and derived hashes so overlays are regenerable. Derived filenames must not encode evaluator flags into scorer features. Operational loader receives only a replay-root/event manifest without attack schedule/masks; evaluator join is separately sealed.

Log every sender event, including unchanged companions and unsupported intervals. Onset/offset markings are added to plots only after prediction hashes are frozen. A cloud outside the crop or count-preserving evasion is not quietly removed from the denominator. If a selected region is empty, the attempted intervention is ineffective, not a successful removal experiment.

## Benign controls and deferred attacks

Always retain natural clean viewpoint changes, moving content, sparse returns and recording gaps. Post-freeze labels may annotate moving-object examples but cannot mask scoring inputs. R03 defines synthetic benign stresses with unchanged base truth: independent coordinate noise sigma={.02,.10} m; pose/calibration perturbation translation {.05,.20} m and yaw {.2,1} degrees in the *assumed* adapter; source-clock skew ±{10,50} ms in the modeled alignment path. These are controlled uncertainty scenarios, not measured dataset error distributions. Keep them separate from clean fit/calibration and from malicious point overlays, and report false alarms and abstentions. Raw downsampling can be a benign sensor-degradation control, paired with removal to demonstrate observational equivalence rather than distinguish intent by flag.

Primary point-only runs leave all metadata unchanged. Pose/timestamp spoofing is deferred until verified semantics and control/independence assumptions justify it. Temporal bursts and sustained overlays are core; broad adaptive optimization, collusion, Sybil, physical laser realism and network attacks are deferred. No bandwidth-policy dependency remains.

Storage: keep one clean archive/extraction and one active derived episode; cache compact raw/score records, regenerate other overlays from hashes/manifests, and declare retention before deleting expendable derived scratch. Keep all failures and exact regeneration recipes; never delete original evidence. Bound CPU/RSS/peak disk in each run and record deviations before increasing scope.
