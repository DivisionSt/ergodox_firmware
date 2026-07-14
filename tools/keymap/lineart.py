"""Regenerate the ASCII lineart comment blocks in config/slicemk_ergodox.keymap.

The lineart is the box-drawing // comments above each layer's bindings that
visually depict the keyboard layout. They drift from the real bindings because
nothing previously generated or checked them. This script fixes that.

    python3 tools/keymap/lineart.py           # dry run: print unified diff
    python3 tools/keymap/lineart.py --write   # rewrite the keymap in place
    python3 tools/keymap/lineart.py --check   # exit 1 if regen would change file

Design:
- Fixed 7-slot column grid per half so right halves align on a common vertical
  seam regardless of how many real keys a row has.
- Binding tokens padded to their slot's character column so each &token sits
  directly under its lineart cell.
- Binding tokens re-emitted VERBATIM (only surrounding whitespace changes).
- Cell labels: "[N] LABEL" where N is the 1-indexed physical position.
- Cell width: auto-sized per layer to the longest label in that layer.
- Home row (6|6): slot 7 left / slot 1 right are empty-box holes (real keys
  exist above and below; the hole is geometrically forced).
- Bottom row (5|5): border notches inward — no empty boxes between 59 and 60.
- 2u thumb keys (ZMK pos 69/70 left, 73/74 right): lineart pipes extend
  downward so the cells look 2u tall. Binding tokens keep their natural source
  grouping (line B = 69 70 71 / 72 73 74, line C = 75 / 76) — 2u-ness is
  lineart decoration only.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import KEY_COUNT, ZMK_KEYMAP, load_tsv
from layers import display
from parse_zmk import parse_zmk

# ── Label overrides ───────────────────────────────────────────────────────────

def _load_label_overrides() -> dict[str, str]:
    rows = load_tsv("lineart_labels.tsv")
    return {r["token"]: r["label"] for r in rows}


_OVERRIDES: dict[str, str] | None = None


def _label(token: str) -> str:
    global _OVERRIDES
    if _OVERRIDES is None:
        _OVERRIDES = _load_label_overrides()
    return _OVERRIDES.get(token, display(token))


def _cell_label(pos: int, token: str) -> str:
    return f"[{pos}] {_label(token)}"


# ── Per-layer cell width ──────────────────────────────────────────────────────

def _layer_cell_width(tokens: list[str]) -> int:
    """Cell width w: enough for the widest label OR the widest token (whichever is larger).
    The slot stride is w+3, which must exceed the longest token to prevent overlap."""
    label_w = max(len(_cell_label(p, tokens[p - 1])) for p in range(1, KEY_COUNT + 1))
    token_w = max(len(t) for t in tokens)
    # stride = w+3; need stride > token_w, so w >= token_w - 2
    return max(label_w, token_w - 2)


# ── Box-drawing primitives ────────────────────────────────────────────────────

def _h(w: int) -> str:
    return "─" * (w + 2)


def _pad(text: str, w: int) -> str:
    return text[:w].center(w)


# ── Fixed-grid geometry ───────────────────────────────────────────────────────
#
# Every row is rendered as a 7-slot left half and 7-slot right half.  Slots
# that have no physical key are either an empty box (interior hole) or omitted
# from the border (notch at the outer edge).
#
# Row occupancy — real positions that map to each slot (None = no key):
#   slot index: 0   1   2   3   4   5   6    (7 slots per half)
ROW_SLOTS = [
    # left positions,         right positions
    ([1,  2,  3,  4,  5,  6,  7],  [8,  9,  10, 11, 12, 13, 14]),  # row 0: 7|7
    ([15, 16, 17, 18, 19, 20, 21], [22, 23, 24, 25, 26, 27, 28]),  # row 1: 7|7
    ([29, 30, 31, 32, 33, 34, None], [None, 35, 36, 37, 38, 39, 40]),  # row 2: home 6|6
    ([41, 42, 43, 44, 45, 46, 47], [48, 49, 50, 51, 52, 53, 54]),  # row 3: 7|7
    ([55, 56, 57, 58, 59, None, None], [None, None, 60, 61, 62, 63, 64]),  # row 4: bottom 5|5
]

GAP = "      "  # 6-space gap between left and right halves
GAP_W = len(GAP)


# ── Absolute column grid ──────────────────────────────────────────────────────
#
# Every line — borders, labels, AND binding code — shares one fixed grid so the
# two halves always align on a common vertical seam.  Columns are 0-based char
# indices into the rendered line (the "//│" prefix occupies cols 0-2).
#
#   left  border of slot k : 2 + k*(w+3)         interior (token/label) : +1
#   right border of slot k : <left border 7> + GAP_W + 1 + k*(w+3)
#
# w+2 is the cell interior width (matches _h(w)); +1 is the cell separator.

def _lbc(slot: int, w: int) -> int:
    """Column of the left-half border glyph (│ ├ ┼ …) at border index `slot`."""
    return 2 + slot * (w + 3)


def _rbc(slot: int, w: int) -> int:
    """Column of the right-half border glyph at border index `slot`."""
    return _lbc(7, w) + GAP_W + 1 + slot * (w + 3)


def _lic(slot: int, w: int) -> int:
    """Column where a left-half token/label cell interior starts."""
    return _lbc(slot, w) + 1


def _ric(slot: int, w: int) -> int:
    """Column where a right-half token/label cell interior starts."""
    return _rbc(slot, w) + 1


def _binding_line(placements: list[tuple[int, str]], w: int) -> str:
    """Render one binding-code line: place each (column, token) onto a blank
    buffer at its absolute column, then rstrip trailing space."""
    width = _ric(7, w) + 40
    buf = [" "] * width
    for col, tok in placements:
        for i, ch in enumerate(tok):
            if 0 <= col + i < width:
                buf[col + i] = ch
    return "".join(buf).rstrip()


def _binding_row(left_slots: list, right_slots: list, tokens: list[str], w: int) -> str:
    """Emit one binding code line with tokens at their fixed grid columns."""
    placements = []
    for slot, pos in enumerate(left_slots):
        if pos is not None:
            placements.append((_lic(slot, w), tokens[pos - 1]))
    for slot, pos in enumerate(right_slots):
        if pos is not None:
            placements.append((_ric(slot, w), tokens[pos - 1]))
    return _binding_line(placements, w)


def _label_row(left_slots: list, right_slots: list, tokens: list[str], w: int,
               left_open: str = "│", right_close: str = "│") -> str:
    """Emit one //│ label comment line."""
    def cell(pos):
        if pos is None:
            return f" {'':>{w}} "  # empty box interior
        return f" {_pad(_cell_label(pos, tokens[pos - 1]), w)} "

    left_cells = "│".join(cell(p) for p in left_slots)
    right_cells = "│".join(cell(p) for p in right_slots)
    return f"//{left_open}" + left_cells + f"│{GAP}│" + right_cells + f"{right_close}"


def _top_border(left_slots: list, right_slots: list, w: int,
                left_top: str = "├", right_top: str = "┐",
                sep_left: str = "┬", sep_right: str = "┬",
                left_right_close: str = "╭", right_right_close: str = "┐",
                is_first_row: bool = False) -> str:
    """Emit one border line for a row.  Only draws segments for slots that have keys or
    are interior holes (home-row slot 7 left / slot 1 right)."""
    # For left: always 7 segments.  For right: always 7 segments.
    # The first-row top uses ╭/┐; subsequent rows use ├/┤ (mid-border).
    pass


def _border_segments(slots: list, w: int) -> list[str]:
    """Return list of 7 segment strings (each is _h(w)), for a 7-slot half."""
    return [_h(w)] * 7


# ── Main body renderer ────────────────────────────────────────────────────────

def _render_body(tokens: list[str], w: int) -> list[str]:
    """
    Render the 5 main body rows.  Fixed 7-slot grid per half.

    Home row (row 2): slot 7 left / slot 1 right are None (no physical key).
    The border still draws those slots as empty boxes; the label line shows an
    empty interior.  This is the geometrically correct interior hole.

    Bottom row (row 4): slots 5-6 left / slots 0-1 right are None.  Border
    notches inward (╯/╰) so no empty boxes appear between 59 and 60.
    """
    out = []
    h = _h(w)

    for row_idx, (left_slots, right_slots) in enumerate(ROW_SLOTS):
        # Compute which left/right slots are "real" (have a key or are interior holes).
        # Interior hole: slot is None but is NOT at the outer edge of its half.
        # Bottom row: the None slots at 5-6 left and 0-1 right are outer-edge → notch.

        if row_idx == 4:
            # Bottom row: 5 keys per side (left slots 0-4, right slots 2-6) on the
            # 7-grid; the inner two slots per half stay open below row 3.
            left_real = left_slots[:5]   # [55,56,57,58,59]
            right_real = right_slots[2:] # [60,61,62,63,64]

            # Border (between row 3 and the bottom row).  All 7 columns carry the
            # bottom edge of row 3's keys; junctions step where the 5-key bottom
            # row ends (┤ after slot 4 left / before slot 2 right).
            left_border = (
                "├" + h + "┼" + h + "┼" + h + "┼" + h + "┼"
                + h + "┤" + h + "┼" + h + "┤"
            )
            right_border = (
                "├" + h + "┼" + h + "┼" + h + "┼" + h + "┼"
                + h + "┤" + h + "┤" + h + "┤"
            )
            out.append(f"//{left_border}{GAP}{right_border}")
            # Bindings
            out.append(_binding_row(left_real + [None, None], [None, None] + right_real, tokens, w))
            # Labels: 5 cells per half on the grid, open middle spanning the four
            # empty inner slots + gap.
            left_cells = "│".join(f" {_pad(_cell_label(p, tokens[p-1]), w)} " for p in left_real)
            right_cells = "│".join(f" {_pad(_cell_label(p, tokens[p-1]), w)} " for p in right_real)
            mid = " " * (_rbc(2, w) - (3 + len(left_cells) + 1))
            out.append(f"//│{left_cells}│{mid}│{right_cells}│")

        elif row_idx == 2:
            # Home row: left slots 0-5 real + slot 6 is hole; right slot 0 is hole + slots 1-6 real.
            left_real = left_slots[:6]   # [29..34]
            right_real = right_slots[1:] # [35..40]

            # Border (between row 1 and home): 6 bordered cells per half, then the
            # interior hole is left OPEN at top (notch ┤ … ├, blank hole interior).
            hole = " " * (w + 2)
            left_border = "┼".join(h for _ in range(6))
            right_border = "┼".join(h for _ in range(6))
            out.append(
                f"//├{left_border}┤{hole}│{GAP}│{hole}├{right_border}┤"
            )
            # Bindings: pad 6 real tokens; hole slot gets spaces
            out.append(_binding_row(left_slots, right_slots, tokens, w))
            # Labels: 6 real + 1 empty on left; 1 empty + 6 real on right
            def home_cell(pos):
                if pos is None:
                    return f" {_pad('', w)} "
                return f" {_pad(_cell_label(pos, tokens[pos-1]), w)} "
            left_cells = "│".join(home_cell(p) for p in left_slots)
            right_cells = "│".join(home_cell(p) for p in right_slots)
            out.append(f"//│" + left_cells + f"│{GAP}│" + right_cells + "│")

        else:
            # Full 7|7 rows (rows 0, 1, 3).
            if row_idx == 0:
                l_open, l_join, l_close = "├", "┬", "┐"
                r_open, r_join, r_close = "╭", "┬", "┐"
            else:
                l_open, l_join, l_close = "├", "┼", "┤"
                r_open, r_join, r_close = "├", "┼", "┤"

            border = l_join.join(h for _ in range(7))
            rborder = r_join.join(h for _ in range(7))
            out.append(
                f"//{l_open}" + border + f"{l_close}"
                + GAP
                + f"{r_open}" + rborder + f"{r_close}"
            )
            out.append(_binding_row(left_slots, right_slots, tokens, w))
            left_cells = "│".join(f" {_pad(_cell_label(p, tokens[p-1]), w)} " for p in left_slots)
            right_cells = "│".join(f" {_pad(_cell_label(p, tokens[p-1]), w)} " for p in right_slots)
            out.append(f"//│" + left_cells + f"│{GAP}│" + right_cells + "│")

    # Bottom border after row 4 (5|5): closes the 5 keys per half, with the four
    # inner slots + gap left open between the ╯ and the ╰.
    left5 = "╰" + "┴".join(h for _ in range(5)) + "╯"
    right5 = "╰" + "┴".join(h for _ in range(5)) + "╯"
    mid = " " * (_rbc(2, w) - (2 + len(left5)))
    out.append(f"//{left5}{mid}{right5}")

    return out


# ── Thumb cluster renderer ────────────────────────────────────────────────────
#
# Physical layout (positions in ZMK order):
#
#   Left thumb                Right thumb
#   ╭───────┬───────╮         ╭───────┬───────╮
#   │  65   │  66   │         │  67   │  68   │
#   ├───────┼───────┼───────╮ ╭───────┼───────┼───────┤
#   │       │       │  71   │ │  72   │       │       │
#   │  69   │  70   ├───────┤ ├───────┤  73   │  74   │
#   │ (2u)  │ (2u)  │  75   │ │  76   │ (2u)  │ (2u)  │
#   ╰───────┴───────┴───────╯ ╰───────┴───────┴───────╯
#
# Binding code groupings (must NOT be reordered):
#   line A: tokens[64] tokens[65]    tokens[66] tokens[67]   (pos 65,66 | 67,68)
#   line B: tokens[68] tokens[69] tokens[70]    tokens[71] tokens[72] tokens[73]  (69,70,71|72,73,74)
#   line C:            tokens[74]               tokens[75]   (75 | 76)
#
# The 2u cell height is purely lineart: pipes on 69/70/73/74 extend past the
# 71/75 (72/76) divider line.  Binding lines keep the groupings above.

def _render_thumbs(tokens: list[str], w: int) -> list[str]:
    h = _h(w)
    out = []

    def lbl(pos):
        return _pad(_cell_label(pos, tokens[pos - 1]), w)

    blank = _pad("", w)
    ind_a = " " * (5 * (w + 3))   # line-A box opens at left border slot 5
    ind_b = " " * (4 * (w + 3))   # 2u block opens at left border slot 4

    # ── Line A: top 1u pairs (65,66 | 67,68), inner two slots per half ────────
    out.append(f"//{ind_a}╭{h}┬{h}╮{GAP}╭{h}┬{h}╮")
    out.append(_binding_line([
        (_lic(5, w), tokens[64]), (_lic(6, w), tokens[65]),
        (_ric(0, w), tokens[66]), (_ric(1, w), tokens[67]),
    ], w))
    out.append(f"//{ind_a}│ {lbl(65)} │ {lbl(66)} │{GAP}│ {lbl(67)} │ {lbl(68)} │")

    # ── 2u block: left slots 4,5,6 (69,70,71) | right slots 0,1,2 (72,73,74) ──
    # Top border
    out.append(f"//{ind_b}╭{h}┼{h}┼{h}┤{GAP}├{h}┼{h}┼{h}╮")
    # Line B bindings (69,70,71 | 72,73,74)
    out.append(_binding_line([
        (_lic(4, w), tokens[68]), (_lic(5, w), tokens[69]), (_lic(6, w), tokens[70]),
        (_ric(0, w), tokens[71]), (_ric(1, w), tokens[72]), (_ric(2, w), tokens[73]),
    ], w))
    # Top interior row: 71/74 labels sit here; 69/70/72/73 span 2u below.
    out.append(f"//{ind_b}│ {lbl(69)} │ {lbl(70)} │ {lbl(71)} │{GAP}│ {lbl(72)} │ {lbl(73)} │ {lbl(74)} │")
    # Middle separator: 69/70 & 73/74 stay open (2u); the inner 71/75 & 72/76 split.
    out.append(f"//{ind_b}│ {blank} │ {blank} ├{h}┤{GAP}├{h}┤ {blank} │ {blank} │")
    # Line C bindings (75 | 76) — left slot 6, right slot 0.
    out.append(_binding_line([(_lic(6, w), tokens[74]), (_ric(0, w), tokens[75])], w))
    # Bottom interior row: 75/76 labels.
    out.append(f"//{ind_b}│ {blank} │ {blank} │ {lbl(75)} │{GAP}│ {lbl(76)} │ {blank} │ {blank} │")
    # Bottom border
    out.append(f"//{ind_b}╰{h}┴{h}┴{h}╯{GAP}╰{h}┴{h}┴{h}╯")

    return out


# ── Bootloader banner ─────────────────────────────────────────────────────────

BOOT_BANNER_WIDTH = 80


def _render_boot_banner(boot_token: str) -> list[str]:
    label = _label(boot_token)
    inner = BOOT_BANNER_WIDTH - 2
    return [
        f"//╭{'─' * inner}╮",
        f"  {boot_token}",
        f"//│ {label.ljust(inner - 2)} │",
    ]


# ── Assemble one layer ────────────────────────────────────────────────────────

def render_layer(index: int, name: str, boot_token: str, tokens: list[str]) -> list[str]:
    w = _layer_cell_width(tokens)
    out = []
    out.extend(_render_boot_banner(boot_token))
    out.extend(_render_body(tokens, w))
    out.extend(_render_thumbs(tokens, w))
    return out


# ── Parse the source and splice in regenerated blocks ────────────────────────

_LAYER_RE = re.compile(
    r"(layer_\d+\s*\{[^{]*?bindings\s*=\s*<)(.*?)(>\s*;)",
    re.DOTALL,
)


def _generate(source: str) -> str:
    zmk = parse_zmk()

    def replace_block(m: re.Match) -> str:
        prefix = m.group(1)
        suffix = m.group(3)
        lm = re.search(r"layer_(\d+)", prefix)
        if not lm:
            return m.group(0)
        idx = int(lm.group(1))
        if idx not in zmk:
            return m.group(0)
        layer = zmk[idx]
        rendered = render_layer(idx, layer.name, layer.bindings[0], layer.keys)
        inner = "\n" + "\n".join(rendered) + "\n\t\t\t"
        return prefix + inner + suffix

    return _LAYER_RE.sub(replace_block, source)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="rewrite keymap in place")
    ap.add_argument("--check", action="store_true", help="exit 1 if regen would change file")
    ap.add_argument("--path", type=Path, default=ZMK_KEYMAP)
    args = ap.parse_args()

    original = args.path.read_text(encoding="utf-8")
    generated = _generate(original)

    if args.check:
        if original != generated:
            print("lineart.py --check: lineart is out of date (run --write to fix)", file=sys.stderr)
            sys.exit(1)
        print("lineart.py --check: lineart is up to date")
        return

    if args.write:
        args.path.write_text(generated, encoding="utf-8")
        print(f"Wrote {args.path}")
        return

    diff = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        generated.splitlines(keepends=True),
        fromfile=str(args.path),
        tofile=str(args.path) + " (regen)",
    ))
    if not diff:
        print("No changes.")
    else:
        sys.stdout.writelines(diff)


if __name__ == "__main__":
    main()
