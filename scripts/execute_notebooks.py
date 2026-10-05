"""Run only the invoked S00 notebook and preserve its evidence bundle."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from valid_point.provenance import bootstrap_run  # noqa: E402


if __name__ == "__main__":
    run_dir = bootstrap_run(ROOT)
    print(run_dir)
    print((run_dir / "gate.md").read_text(encoding="utf-8"))
    if "PASS" not in (run_dir / "gate.md").read_text(encoding="utf-8"):
        raise SystemExit(1)
