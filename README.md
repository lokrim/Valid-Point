# Valid Point

Valid Point is a bounded research replay of recorded cooperative LiDAR observations. The package is `valid_point`. The [current planning index](planning/README.md), [research contract](planning/01_research_contract.md), and [evidence audit](planning/evidence_audit.md) govern the R01–R07 sequence. Earlier S00–S04 runs are retained as historical constructed or infrastructure evidence; their reported numbers are not Mixed Signals performance.

## Current stage

R01 inspected the authorized pinned `mini_7` archive and recorded [GR1](artifacts/20261008T192922Z-R01/gate.md). R02 implements a causal reader, sensor-relative raw count cells D, and conditional directed geometric novelty G on the extracted development window. Its run produces raw measurements and unknowns; it does not fit final references, calibrate alarms, run interventions, or acquire comparison/final data. `top` and `dome` are two streams from one RSU physical principal. The source timestamps are recording metadata; receiver arrival is an explicit idealized replay assumption.

R02 entry point (one stage only):

```sh
.venv/bin/python scripts/inspect_causal_factors.py
```

The runner uses [the exact R02 config](configs/causal_factors.json), tests `tests/`, executes [the R02 notebook](notebooks/R02_causal_factors.ipynb) in a fresh kernel, and creates an immutable `artifacts/<timestamp>-R02/` run with full tables, figures, hashes, log, and gate. It reads only already extracted `mini_7` PCDs and odometry CSVs under this repository. Output references and calibration IDs remain null at R02. Do not treat one contiguous `mini_7` window as independent training scenes.

The S runners and their notebooks are historical and should be used only to reproduce their original scope. They do not enforce the R02 operational boundary. See [runner documentation](scripts/README.md) and [notebook plan](planning/08_notebooks.md).

## Environment

The project uses CPython 3.14 in `.venv` for its saved runs. Install the hashed lock if creating the environment anew:

```sh
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python --require-hashes -r requirements.lock
```

Core implementation is in `src/valid_point/`; old S arithmetic remains available. `data/` and `artifacts/` are local ignored inputs and evidence. No detector framework is part of this stage. The dataset license and pinned source are recorded in [source verification](planning/sources.md).
