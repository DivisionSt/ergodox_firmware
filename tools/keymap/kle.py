"""Inspect and lint the hand-curated KLE file (kle/divisionst_ergodox.json).

This tool LOCATES and DECODES — it never rewrites the file. The KLE is
hand-curated; edits must be surgical text replacements (via the Edit tool) of a
single legend string, not a re-serialization of the JSON (which would reflow the
author's formatting).

    python3 tools/keymap/kle.py --lint
    python3 tools/keymap/kle.py --show Y        # find keys whose base legend is Y
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass

from common import KLE_FILE, load_tsv

MAX_SLOTS = 12
SLOT_NAMES = [
    "top-left", "bottom-left", "top-right", "bottom-right",
    "front-left", "front-right", "center-left", "center-right",
    "top-center", "center", "bottom-center", "front-center",
]


@dataclass
class KleKey:
    row: int
    col: int            # index of this key within its row
    legends: list[str]  # up to 12 slots
    colors: list[str]   # up to 12 slots (the active `t` split)

    @property
    def base(self) -> str:
        return self.legends[0] if self.legends else ""


def load_keys(path=KLE_FILE) -> list[KleKey]:
    data = json.loads(path.read_text(encoding="utf-8"))
    keys: list[KleKey] = []
    for r, row in enumerate(data):
        if not isinstance(row, list):
            continue  # metadata object
        current_t = ""
        col = 0
        for item in row:
            if isinstance(item, dict):
                if "t" in item:
                    current_t = item["t"]
            elif isinstance(item, str):
                keys.append(KleKey(
                    row=r, col=col,
                    legends=item.split("\n"),
                    colors=current_t.split("\n") if current_t else [],
                ))
                col += 1
    return keys


def slot_layer_table() -> dict[tuple[int, str], tuple[str, str]]:
    """(slot, color) -> (layer, note)."""
    out = {}
    for row in load_tsv("kle_encoding.tsv"):
        out[(int(row["slot"]), row["color"])] = (row["layer"], row["note"])
    return out


def lint(path=KLE_FILE) -> list[str]:
    issues: list[str] = []
    try:
        keys = load_keys(path)
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    for k in keys:
        if len(k.legends) > MAX_SLOTS:
            issues.append(f"row {k.row} key {k.col} ({k.base!r}): "
                          f"{len(k.legends)} legend slots > {MAX_SLOTS}")
        if k.colors and len(k.colors) > MAX_SLOTS:
            issues.append(f"row {k.row} key {k.col} ({k.base!r}): "
                          f"{len(k.colors)} color slots > {MAX_SLOTS}")
    return issues


def show(base_legend: str, path=KLE_FILE) -> None:
    table = slot_layer_table()
    matches = [k for k in load_keys(path) if k.base == base_legend]
    if not matches:
        print(f"No KLE key with base legend {base_legend!r}.")
        return
    for k in matches:
        print(f"\nKLE key (row {k.row}, position {k.col}) base={k.base!r}")
        for i, legend in enumerate(k.legends):
            if not legend:
                continue
            color = k.colors[i] if i < len(k.colors) else ""
            layer, _ = table.get((i, color), ("?", ""))
            sname = SLOT_NAMES[i] if i < len(SLOT_NAMES) else f"slot{i}"
            print(f"  slot {i:>2} ({sname:<13}) color {color or '—':<9} "
                  f"layer={layer:<7} legend={legend!r}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lint", action="store_true")
    ap.add_argument("--show", metavar="BASE_LEGEND")
    args = ap.parse_args()
    if args.lint:
        problems = lint()
        if problems:
            print("KLE lint found issues:")
            for p in problems:
                print(f"  - {p}")
            raise SystemExit(1)
        print(f"KLE lint OK: {len(load_keys())} keys, all within {MAX_SLOTS} slots.")
    elif args.show:
        show(args.show)
    else:
        ap.print_help()
