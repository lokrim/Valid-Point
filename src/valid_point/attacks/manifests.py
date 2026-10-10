"""Evaluator-only attempt ledgers, separate from operational event inputs."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class Attempt:
    episode: str
    cloud_id: str
    family: str
    severity: float
    schedule: str
    source_ns: int
    base_sha256: str
    seed_key: str
    target_cell: str | None
    intended_count: int
    selected_count: int
    injected_changed_count: int
    failed_count: int
    injection_reason: str
    selection_ledger: str
    selection_ledger_sha256: str
    injected_count: int
    derived_sha256: str | None
    reader_status: str
    reader_reason: str
    reread_count: int | None
    realized_changed_rows: int | None
    realized_cell_changes: int | None
    realized_max_displacement_m: float | None
    realized_inside_fraction: float | None

    def as_dict(self) -> dict:
        return asdict(self)
