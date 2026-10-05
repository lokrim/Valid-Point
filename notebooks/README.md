# Notebooks

`00_bootstrap.ipynb` is an unexecuted source notebook. Run it through
`scripts/execute_notebooks.py`; each run saves its executed copy under a new
ignored `artifacts/<run_id>/` directory. Later stages get their own fresh-kernel
notebooks. Use the named deliverables
and visible evidence contract in [the notebook plan](../planning/08_notebooks.md).
Keep computation in `src/valid_point/`; notebooks explain, call, and display it.

S02 sources are `02_kinematics.ipynb`, `02_spatial_surplus.ipynb`, and
`02_availability.ipynb`. Execute them through `scripts/measure_synthetic.py` so
run context and hashes are present. Fully executed copies and all named exports
are linked from that run's `gate.md`; source notebooks intentionally have no
outputs. All cases are deterministic hand fixtures, with no fit or score.
