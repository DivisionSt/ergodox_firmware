"""QMK <-> ZMK parity report.

Compares the overlapping layers (per maps/layer_map.tsv) key-by-key using the
position map and the semantic translator, then compares combos by physical
chord. ZMK-only layers (game/app bases, underglow) are reported as intentional,
never as drift.

Usage:
    python tools/keymap/parity.py              # layers + combos
    python tools/keymap/parity.py --summary    # counts only
    python tools/keymap/parity.py --layer mac
    python tools/keymap/parity.py --combos     # combo report only
    python tools/keymap/parity.py --layers-only
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

import translate
from common import KEY_COUNT, load_layer_map, load_position_map
from parse_qmk import parse_qmk, parse_qmk_combos
from parse_zmk import parse_layer_defines, parse_zmk, parse_zmk_combos
from translate import Category, canon_qmk, canon_zmk, equivalent


@dataclass
class KeyDiff:
    pos: int          # QMK physical position
    qmk: str
    zmk: str
    category: Category


@dataclass
class ComboDiff:
    positions: list[int]      # ZMK physical positions forming the chord
    zmk_name: str | None      # None when QMK has a combo ZMK does not
    zmk_binding: str | None
    zmk_layers: str
    qmk_name: str | None      # None when ZMK has a combo QMK does not
    qmk_action: str | None
    qmk_gate: str
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


def _qmk_combo_positions(triggers, qmk_layers, base_indices, pos_map) -> list[int] | None:
    """Resolve a QMK combo's trigger keycodes to the ZMK positions they occupy.

    QMK matches combos on the post-layer-resolution keycode rather than on
    physical position, so the chord has to be located by searching the base
    layers. The first base layer on which every trigger appears exactly once
    wins; ambiguity (a keycode present twice, or missing everywhere) yields None
    so the caller can report it rather than guess.
    """
    for idx in base_indices:
        keys = qmk_layers[idx].keys
        found: list[int] = []
        for trigger in triggers:
            hits = [p for p in range(1, KEY_COUNT + 1) if keys[p - 1] == trigger]
            if len(hits) != 1:
                found = []
                break
            found.append(hits[0])
        if found:
            return sorted(pos_map[p] for p in found)
    return None


def build_combo_report(qmk_path=None, zmk_path=None) -> list[ComboDiff]:
    """Compare combos across the two firmwares, keyed by physical chord.

    Matching is positional rather than by keycode: ZMK combos are natively
    position-based, and position 29 already differs by keycode (QMK KC_F24 vs
    ZMK &none) while being the same physical chord.

    Layer scope is reported for context but never drives the category. QMK
    scopes combos with combo_should_trigger() while ZMK uses an explicit
    `layers` property, and the two do not express the same sets — QMK's base
    layers are transient toggles, so "not base-win" is the robust QMK spelling
    of what ZMK writes as "base-mac".
    """
    qmk_layers = parse_qmk(qmk_path) if qmk_path else parse_qmk()
    qmk_combos = parse_qmk_combos(qmk_path) if qmk_path else parse_qmk_combos()
    zmk_combos = parse_zmk_combos(zmk_path) if zmk_path else parse_zmk_combos()
    # &tog L_EXT_NAV and friends need the layer #defines to canonicalize.
    src = (zmk_path or __import__("common").ZMK_KEYMAP).read_text(encoding="utf-8")
    translate.ZMK_LAYER_DEFINES = parse_layer_defines(src)

    pos_map = load_position_map()
    base_indices = [p.qmk_index for p in load_layer_map()
                    if p.overlap and p.qmk_index is not None and p.qmk_index <= 2]

    resolved: list[tuple] = []
    for combo in qmk_combos:
        positions = _qmk_combo_positions(combo.triggers, qmk_layers, base_indices, pos_map)
        resolved.append((combo, positions))

    diffs: list[ComboDiff] = []
    claimed: set[int] = set()
    for zc in zmk_combos:
        chord = sorted(zc.key_positions)
        candidates = [(c, p) for c, p in resolved if p == chord]
        match = next(
            (c for c, _ in candidates
             if equivalent(c.action, zc.binding) is Category.MATCH),
            None,
        )
        if match is not None:
            claimed.add(match.index)
            diffs.append(ComboDiff(
                positions=chord, zmk_name=zc.name, zmk_binding=zc.binding,
                zmk_layers=",".join(zc.layers) or "all",
                qmk_name=match.name, qmk_action=match.action,
                qmk_gate=match.gate or "global", category=Category.MATCH))
        elif candidates:
            # Same physical chord exists on the QMK side but emits something else.
            near = candidates[0][0]
            claimed.add(near.index)
            diffs.append(ComboDiff(
                positions=chord, zmk_name=zc.name, zmk_binding=zc.binding,
                zmk_layers=",".join(zc.layers) or "all",
                qmk_name=near.name, qmk_action=near.action,
                qmk_gate=near.gate or "global", category=Category.DRIFT))
        else:
            diffs.append(ComboDiff(
                positions=chord, zmk_name=zc.name, zmk_binding=zc.binding,
                zmk_layers=",".join(zc.layers) or "all",
                qmk_name=None, qmk_action=None, qmk_gate="-",
                category=Category.UNMAPPED))

    for combo, positions in resolved:
        if combo.index in claimed:
            continue
        diffs.append(ComboDiff(
            positions=positions or [], zmk_name=None, zmk_binding=None,
            zmk_layers="-", qmk_name=combo.name, qmk_action=combo.action,
            qmk_gate=combo.gate or "global", category=Category.UNMAPPED))
    return diffs


def _fmt_combo(d: ComboDiff) -> str:
    tag = {Category.MATCH: "ok   ", Category.DRIFT: "DRIFT",
           Category.UNMAPPED: "UNMAP", Category.BLANK_DIFF: "blank"}[d.category]
    chord = "+".join(str(p) for p in d.positions) or "??"
    zmk = f"{d.zmk_name} {d.zmk_binding}" if d.zmk_name else "(none)"
    qmk = f"{d.qmk_name} {d.qmk_action}" if d.qmk_name else "(none)"
    line = f"    [{tag}] {chord:<8} ZMK {zmk}"
    if d.category is not Category.MATCH:
        return f"{line}\n                       QMK {qmk}"
    return line


def print_combo_report(verbose: bool = True) -> int:
    diffs = build_combo_report()
    counts = {c: sum(1 for d in diffs if d.category is c) for c in Category}
    drift = counts[Category.DRIFT]
    unmapped = counts[Category.UNMAPPED]
    flag = "OK " if (drift == 0 and unmapped == 0) else "!! "
    print(f"\n{flag}combos  match={counts[Category.MATCH]} drift={drift} "
          f"unmapped={unmapped}")
    for d in diffs:
        if d.category is Category.MATCH and not verbose:
            continue
        print(_fmt_combo(d))
    print("    (layer scope is informational: QMK gates with combo_should_trigger(),")
    print("     ZMK with an explicit `layers` property; the two are not directly comparable)")
    return 1 if (drift or unmapped) else 0


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


def print_report(layer_filter: str | None = None, summary_only: bool = False,
                 combos: bool = True) -> int:
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

    combo_status = print_combo_report(verbose=not summary_only) if combos else 0

    print("\n" + "-" * 42)
    print(f"TOTAL  match={total[Category.MATCH]} drift={total[Category.DRIFT]} "
          f"unmapped={total[Category.UNMAPPED]} blank-diff={total[Category.BLANK_DIFF]}")
    print(f"Intentional ZMK-only layers (not drift): {', '.join(zmk_only)}")
    # Non-zero exit if real drift or unmapped tokens exist, on keys or on combos.
    layer_status = 1 if (total[Category.DRIFT] or total[Category.UNMAPPED]) else 0
    return 1 if (layer_status or combo_status) else 0


if __name__ == "__main__":
    sys.path.insert(0, ".")
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true", help="counts only, no per-key diffs")
    ap.add_argument("--layer", help="filter to one layer (canonical slug or name)")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--combos", action="store_true", help="combo report only")
    group.add_argument("--layers-only", action="store_true", help="skip the combo report")
    args = ap.parse_args()
    if args.combos:
        raise SystemExit(print_combo_report())
    raise SystemExit(print_report(layer_filter=args.layer, summary_only=args.summary,
                                  combos=not args.layers_only))
