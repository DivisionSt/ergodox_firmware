"""Generate LAYERS.md: a ZMK-superset map of every layer, marking which layers
QMK also carries and where the two firmwares diverge.

    python3 tools/keymap/layers.py            # print to stdout
    python3 tools/keymap/layers.py --write    # write LAYERS.md at repo root
"""

from __future__ import annotations

import argparse
import re

import translate
from common import REPO_ROOT, ZMK_KEYMAP, load_layer_map
from parity import build_report
from parse_zmk import parse_layer_defines, parse_zmk

# Physical row groupings by position (1..76). Left | right per row.
ROWS = [
    (range(1, 8), range(8, 15)),     # row 1: 7 | 7
    (range(15, 22), range(22, 29)),  # row 2: 7 | 7
    (range(29, 35), range(35, 41)),  # row 3: 6 | 6
    (range(41, 48), range(48, 55)),  # row 4: 7 | 7
    (range(55, 60), range(60, 65)),  # row 5: 5 | 5
]
# Thumb clusters by physical position (see position_map.tsv / matrix dtsi).
THUMB_L = [(65, 66), (69, 70, 71), (75,)]
THUMB_R = [(67, 68), (72, 73, 74), (76,)]

# Keyed by canonical slug (see maps/layer_map.tsv).
PURPOSE = {
    "mac": "Default macOS base layer.",
    "fortnite": "Fortnite gaming base (home only).",
    "minecraft": "Minecraft gaming base (home only).",
    "gaming": "Generic gaming base (home only).",
    "win": "Windows base layer.",
    "sketchup": "SketchUp application base (home only).",
    "old": "Legacy/fallback base layer.",
    "nav": "Navigation + F-keys (mac).",
    "num": "Number pad + symbols (mac).",
    "wnav": "Navigation + F-keys (Windows).",
    "wnum": "Number pad + symbols (Windows).",
    "func": "Function-key cluster.",
    "mouse": "Mouse movement, scroll, and clicks.",
    "layers": "Layer switching and device/config controls.",
    "underglow": "RGB underglow testing (home only).",
    "blank": "Unused transparent layer.",
}

# Short symbols for modifiers and media keys used in display labels.
_MOD_SYM = {"LGUI": "⌘", "LG": "⌘", "LCMD": "⌘", "LCTRL": "⌃", "LC": "⌃",
            "LALT": "⌥", "LA": "⌥", "LSHFT": "⇧", "LS": "⇧",
            "RGUI": "⌘", "RG": "⌘", "RCMD": "⌘", "RCTRL": "⌃", "RC": "⌃", "RSHFT": "⇧"}
_ATOM_SYM = {"C_PP": "⏯", "C_VOL_UP": "vol+", "C_VOL_DN": "vol-", "C_NEXT": "next",
             "C_PREV": "prev", "C_BRI_INC": "bri+", "C_BRI_DEC": "bri-"}


def _atom_label(atom: str) -> str:
    atom = re.sub(r"^N([0-9])$", r"\1", atom)
    return _ATOM_SYM.get(atom, atom)


def _unwrap(expr: str) -> str:
    """Render a (possibly mod-wrapped) ZMK expression like LC(LG(SPACE))."""
    syms = []
    cur = expr
    while True:
        m = re.fullmatch(r"([A-Z]+)\((.*)\)", cur)
        if not m or m.group(1) not in _MOD_SYM:
            break
        syms.append(_MOD_SYM[m.group(1)])
        cur = m.group(2)
    return "".join(syms) + (_MOD_SYM.get(cur) or _atom_label(cur))


def display(token: str) -> str:
    """Short human label for a ZMK binding."""
    t = token.strip()
    simple = {
        "&trans": "▽", "&none": "·", "&bootloader": "BOOT", "&sys_reset": "RESET",
        "&leader": "LEAD", "&key_repeat": "RPT", "&cmd_tab": "cmdtab",
        "&alt_tab": "alttab", "&caps_word": "CAPS",
    }
    if t in simple:
        return simple[t]
    m = re.fullmatch(r"&kp (.+)", t)
    if m:
        return _unwrap(m.group(1))
    m = re.fullmatch(r"&sk (\w+)", t)
    if m:
        return "sk" + (_MOD_SYM.get(m.group(1)) or ":" + m.group(1).lower())
    m = re.fullmatch(r"&skht (\w+) (\w+)", t)   # tap param is second
    if m:
        return "skht" + (_MOD_SYM.get(m.group(2)) or ":" + m.group(2).lower())
    m = re.fullmatch(r"&t?lt (L_[A-Z0-9_]+) (\w+)", t)
    if m:
        return f"→{m.group(1).replace('L_EXT_', '').replace('L_', '').lower()}/{_atom_label(m.group(2))}"
    m = re.fullmatch(r"&t?mt (\S+(?:\([^ ]*\))?) (\w+)", t)
    if m:
        return f"{_unwrap(m.group(1))}/{_atom_label(m.group(2))}"
    m = re.fullmatch(r"&(to|mo|tog) (L_[A-Z0-9_]+)", t)
    if m:
        op = {"to": "TO", "mo": "MO", "tog": "TOG"}[m.group(1)]
        return f"{op}:{m.group(2).replace('L_BASE_', '').replace('L_', '').lower()}"
    m = re.fullmatch(r"&bt BT_SEL (\d)", t)
    if m:
        return "BT" + m.group(1)
    if t == "&bt BT_CLR":
        return "BTclr"
    m = re.fullmatch(r"&out OUT_(\w+)", t)
    if m:
        return "out:" + m.group(1).lower()
    m = re.fullmatch(r"&mkp (\w+)", t)
    if m:
        return m.group(1).replace("CLK", "clk").lower()
    m = re.fullmatch(r"&m(mv|sc) \w+_(\w+)", t)
    if m:
        return ("mv:" if m.group(1) == "mv" else "scr:") + m.group(2).lower()[:4]
    return t.replace("&", "")[:9]


def _cell(label: str, width: int = 8) -> str:
    return label[:width].center(width)


def render_grid(keys: list[str]) -> str:
    """keys is the 76-entry physical position list (index 0 == position 1)."""
    lines = []
    for left, right in ROWS:
        lcells = " ".join(_cell(display(keys[p - 1])) for p in left)
        rcells = " ".join(_cell(display(keys[p - 1])) for p in right)
        lines.append(f"  {lcells}    {rcells}")
    # Thumbs
    def thumb(cluster):
        return ["  ".join(_cell(display(keys[p - 1])) for p in grp) for grp in cluster]
    lt, rt = thumb(THUMB_L), thumb(THUMB_R)
    lines.append("")
    lines.append("  thumbs   L: " + "  |  ".join(lt))
    lines.append("           R: " + "  |  ".join(rt))
    return "\n".join(lines)


def generate() -> str:
    zmk = parse_zmk()
    translate.ZMK_LAYER_DEFINES = parse_layer_defines(ZMK_KEYMAP.read_text(encoding="utf-8"))
    pairs = load_layer_map()
    by_zmk = {p.zmk_index: p for p in pairs if p.zmk_index is not None}

    # Per-layer QMK drift, keyed by canonical slug.
    reports, _ = build_report()
    drift_by_canon = {
        r.canonical: [d for d in r.diffs if d.category.value in ("drift", "unmapped")]
        for r in reports
    }

    out: list[str] = []
    out.append("# Ergodox layer map\n")
    out.append("> Generated by `tools/keymap/layers.py` from the ZMK keymap "
               "(`config/slicemk_ergodox.keymap`), the home-keyboard superset. "
               "QMK (`DYrAK/`, work) carries the layers marked **QMK ✓**. "
               "Do not hand-edit; regenerate after layout changes.\n")

    out.append("## Layers at a glance\n")
    out.append("| # | Layer | QMK | Purpose |")
    out.append("|---|-------|-----|---------|")
    for idx in sorted(zmk):
        pair = by_zmk.get(idx)
        name = zmk[idx].name
        slug = pair.canonical if pair else name
        has_qmk = "✓" if (pair and pair.overlap) else "—"
        out.append(f"| {idx} | {name} | {has_qmk} | {PURPOSE.get(slug, '')} |")
    out.append("")

    out.append("## Per-layer maps\n")
    for idx in sorted(zmk):
        pair = by_zmk.get(idx)
        name = zmk[idx].name
        slug = pair.canonical if pair else name
        qmk_note = (f"QMK ✓ (`DYrAK` layer {pair.qmk_index}: {pair.qmk_name})"
                    if pair and pair.overlap else "ZMK-only (home keyboard)")
        out.append(f"### {idx}. {name}\n")
        out.append(f"{PURPOSE.get(slug, '')}  \n_{qmk_note}_\n")
        out.append("```")
        out.append(render_grid(zmk[idx].keys))
        out.append("```\n")
        diffs = drift_by_canon.get(slug or "", [])
        if diffs:
            out.append(f"**QMK differs here ({len(diffs)}):**\n")
            for d in diffs:
                out.append(f"- pos {d.pos}: QMK `{d.qmk}` vs ZMK `{d.zmk}`")
            out.append("")
    out.append("---\n")
    out.append("Legend: `▽` transparent · `·` none/blocked · `→x/Y` layer-tap "
               "(hold→layer x, tap→Y) · `sk:` sticky mod · `TO:`/`TOG:` layer "
               "switch · `BT`/`out:` ZMK wireless controls.\n")
    return "\n".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write LAYERS.md at repo root")
    args = ap.parse_args()
    content = generate()
    if args.write:
        (REPO_ROOT / "LAYERS.md").write_text(content, encoding="utf-8")
        print(f"Wrote {REPO_ROOT / 'LAYERS.md'}")
    else:
        print(content)
