"""Shared helpers for the keymap tooling.

Locates repo files, loads the TSV maps, and exposes the layer/position
mappings used by the QMK<->ZMK parity and documentation tools.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

# tools/keymap/common.py -> repo root is two parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]
MAPS_DIR = Path(__file__).resolve().parent / "maps"

# Default source files (the live canonical layouts).
QMK_KEYMAP = REPO_ROOT / "DYrAK" / "keymap.c"
ZMK_KEYMAP = REPO_ROOT / "config" / "slicemk_ergodox.keymap"
KLE_FILE = REPO_ROOT / "kle" / "divisionst_ergodox.json"

# Physical key count of the Ergodox (excludes ZMK's bootloader slot 0).
KEY_COUNT = 76


def load_tsv(name: str) -> list[dict[str, str]]:
    """Load a maps/*.tsv file as a list of row dicts, skipping `#` comments."""
    path = MAPS_DIR / name
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(
            (line for line in fh if not line.startswith("#")),
            delimiter="\t",
        )
        for row in reader:
            rows.append({k: (v.strip() if v else "") for k, v in row.items()})
    return rows


@dataclass(frozen=True)
class LayerPair:
    canonical: str
    qmk_index: int | None
    qmk_name: str
    zmk_index: int | None
    zmk_name: str
    overlap: bool


def load_layer_map() -> list[LayerPair]:
    pairs: list[LayerPair] = []
    for row in load_tsv("layer_map.tsv"):
        qmk_idx = int(row["qmk_index"]) if row["qmk_index"] != "-" else None
        zmk_idx = int(row["zmk_index"]) if row["zmk_index"] != "-" else None
        pairs.append(
            LayerPair(
                canonical=row["canonical"],
                qmk_index=qmk_idx,
                qmk_name=row["qmk_name"],
                zmk_index=zmk_idx,
                zmk_name=row["zmk_name"],
                overlap=row["overlap"] == "yes",
            )
        )
    return pairs


def qmk_index_to_canonical() -> dict[int, str]:
    return {p.qmk_index: p.canonical for p in load_layer_map() if p.qmk_index is not None}


def zmk_index_to_canonical() -> dict[int, str]:
    return {p.zmk_index: p.canonical for p in load_layer_map() if p.zmk_index is not None}


def load_position_map() -> dict[int, int]:
    """Map QMK physical position (1..76) -> ZMK physical position (1..76)."""
    out: dict[int, int] = {}
    for row in load_tsv("position_map.tsv"):
        out[int(row["qmk_pos"])] = int(row["zmk_pos"])
    return out
