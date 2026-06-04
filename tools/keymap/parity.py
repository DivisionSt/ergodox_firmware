"""QMK <-> ZMK parity report.

Compares the overlapping layers (per maps/layer_map.tsv) key-by-key using the
position map and the semantic translator. ZMK-only layers (game/app bases,
underglow) are reported as intentional, never as drift.

Usage:
    python tools/keymap/parity.py            # full report
    python tools/keymap/parity.py --summary  # counts only
    python tools/keymap/parity.py --layer mac
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

import translate
from common import KEY_COUNT, load_layer_map, load_position_map
from parse_qmk import parse_qmk
from parse_zmk import parse_layer_defines, parse_zmk
from translate import Category, canon_qmk, canon_zmk, equivalent


@dataclass
class KeyDiff:
    pos: int          # QMK physical position
    qmk: str
    zmk: str
    category: Category


@dataclass
class LayerReport:
    canonical: str
    qmk_name: str
    zmk_name: str
    diffs: list[KeyDiff] = field(default_factory=list)
    counts: dict[Category, int] = field(default_factory=dict)


def build_report(qmk_path=None, zmk_path=None) -> tuple[list[LayerReport], list[str]]:
    qmk = parse_qmk(qmk_path) if qmk_path else parse_qmk()
    zmk = parse_zmk(zmk_path) if zmk_path else parse_zmk()
    # Wire ZMK layer #defines so the translator can resolve &to/&lt layer names.
    src = (zmk_path or __import__("common").ZMK_KEYMAP).read_text(encoding="utf-8")
    translate.ZMK_LAYER_DEFINES = parse_layer_defines(src)

    pos_map = load_position_map()
    reports: list[LayerReport] = []
    zmk_only: list[str] = []

    for pair in load_layer_map():
        if not pair.overlap:
            if pair.zmk_index is not None:
                zmk_only.append(f"{pair.zmk_name} (zmk layer {pair.zmk_index})")
            continue
        qkeys = qmk[pair.qmk_index].keys
        zkeys = zmk[pair.zmk_index].keys
        rep = LayerReport(pair.canonical, pair.qmk_name, pair.zmk_name)
        rep.counts = {c: 0 for c in Category}
        for qpos in range(1, KEY_COUNT + 1):
            zpos = pos_map[qpos]
            qtok = qkeys[qpos - 1]
            ztok = zkeys[zpos - 1]
            cat = equivalent(qtok, ztok)
            rep.counts[cat] += 1
            if cat is not Category.MATCH:
                rep.diffs.append(KeyDiff(qpos, qtok, ztok, cat))
        reports.append(rep)
    return reports, zmk_only


def _fmt_diff(d: KeyDiff) -> str:
    qc, _ = canon_qmk(d.qmk)
    zc, _ = canon_zmk(d.zmk)
    tag = {
        Category.DRIFT: "DRIFT",
        Category.BLANK_DIFF: "blank",
        Category.UNMAPPED: "UNMAP",
    }[d.category]
    return (f"    [{tag}] pos {d.pos:>2}:  QMK {d.qmk:<24} ({qc})\n"
            f"                   ZMK {d.zmk:<24} ({zc})")


def print_report(layer_filter: str | None = None, summary_only: bool = False) -> int:
    reports, zmk_only = build_report()
    total = {c: 0 for c in Category}
    print("QMK (DYrAK) <-> ZMK (config) parity\n" + "=" * 42)
    for rep in reports:
        if layer_filter and layer_filter not in (rep.canonical, rep.qmk_name, rep.zmk_name):
            continue
        for c in Category:
            total[c] += rep.counts[c]
        drift = rep.counts[Category.DRIFT]
        unmapped = rep.counts[Category.UNMAPPED]
        blank = rep.counts[Category.BLANK_DIFF]
        flag = "OK " if (drift == 0 and unmapped == 0) else "!! "
        print(f"\n{flag}{rep.canonical:<8} (qmk:{rep.qmk_name} / zmk:{rep.zmk_name})"
              f"  match={rep.counts[Category.MATCH]} drift={drift} "
              f"unmapped={unmapped} blank={blank}")
        if not summary_only:
            for d in rep.diffs:
                if d.category is Category.BLANK_DIFF:
                    continue  # blank trans/none differences are informational; hide by default
                print(_fmt_diff(d))

    print("\n" + "-" * 42)
    print(f"TOTAL  match={total[Category.MATCH]} drift={total[Category.DRIFT]} "
          f"unmapped={total[Category.UNMAPPED]} blank-diff={total[Category.BLANK_DIFF]}")
    print(f"Intentional ZMK-only layers (not drift): {', '.join(zmk_only)}")
    # Non-zero exit if real drift or unmapped tokens exist.
    return 1 if (total[Category.DRIFT] or total[Category.UNMAPPED]) else 0


if __name__ == "__main__":
    sys.path.insert(0, ".")
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true", help="counts only, no per-key diffs")
    ap.add_argument("--layer", help="filter to one layer (canonical slug or name)")
    args = ap.parse_args()
    raise SystemExit(print_report(layer_filter=args.layer, summary_only=args.summary))
