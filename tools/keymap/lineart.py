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


def _slot_col(slot: int, w: int) -> int:
    """Character column (0-based, after the leading '  ') for a slot's token start."""
    return slot * (w + 3)  # w+2 cell interior + 1 separator


def _binding_row(left_slots: list, right_slots: list, tokens: list[str], w: int) -> str:
    """Emit one binding code line with tokens padded to their slot columns."""
    # Build a char buffer for left and right halves.
    # Left half: 7 slots, each takes (w+3) chars, total = 7*(w+3) chars.
    half_w = 7 * (w + 3)
    left_buf = [" "] * half_w
    right_buf = [" "] * half_w

    for slot, pos in enumerate(left_slots):
        if pos is None:
            continue
        tok = tokens[pos - 1]
        col = _slot_col(slot, w)
        for i, ch in enumerate(tok):
            if col + i < half_w:
                left_buf[col + i] = ch

    for slot, pos in enumerate(right_slots):
        if pos is None:
            continue
        tok = tokens[pos - 1]
        col = _slot_col(slot, w)
        for i, ch in enumerate(tok):
            if col + i < half_w:
                right_buf[col + i] = ch

    left_str = "".join(left_buf).rstrip()
    right_str = "".join(right_buf).rstrip()
    return "  " + left_str + GAP + right_str


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
            # Bottom row: 5 real keys per side, notch on inner side.
            # Left: slots 0-4 real, 5-6 None (outer/inner edge — notch closes there).
            # Right: slots 0-1 None (notch), 2-6 real.
            left_real = left_slots[:5]   # [55,56,57,58,59]
            right_real = right_slots[2:] # [60,61,62,63,64]

            if row_idx == 0:
                l_open, r_open = "╭", "╭"
                l_join, r_join = "┬", "┬"
                l_close, r_close = "┐", "┐"
            else:
                l_open, r_open = "├", "├"
                l_join, r_join = "┼", "┼"
                l_close, r_close = "┤", "┤"

            # Border
            out.append(
                f"//{l_open}" + l_join.join(h for _ in left_real) + f"{l_close}"
                + GAP
                + f"{r_open}" + r_join.join(h for _ in right_real) + f"{r_close}"
            )
            # Bindings
            out.append(_binding_row(left_real + [None, None], [None, None] + right_real, tokens, w))
            # Labels
            left_cells = "│".join(f" {_pad(_cell_label(p, tokens[p-1]), w)} " for p in left_real)
            right_cells = "│".join(f" {_pad(_cell_label(p, tokens[p-1]), w)} " for p in right_real)
            out.append(f"//│" + left_cells + f"│{GAP}│" + right_cells + "│")

        elif row_idx == 2:
            # Home row: left slots 0-5 real + slot 6 is hole; right slot 0 is hole + slots 1-6 real.
            left_real = left_slots[:6]   # [29..34]
            right_real = right_slots[1:] # [35..40]

            if row_idx == 0:
                l_open, l_join, l_close = "╭", "┬", "┐"
                r_open, r_join, r_close = "╭", "┬", "┐"
            else:
                l_open, l_join, l_close = "├", "┼", "┤"
                r_open, r_join, r_close = "├", "┼", "┤"

            # Border: left has 6 real + 1 empty box slot; right has 1 empty box + 6 real.
            left_border = l_join.join(h for _ in range(7))  # 7 segments including hole
            right_border = r_join.join(h for _ in range(7))
            out.append(
                f"//{l_open}" + left_border + f"{l_close}"
                + GAP
                + f"{r_open}" + right_border + f"{r_close}"
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

    # Bottom border after row 4 (5|5), notched.
    # Connects into the thumb cluster: left closes with ╯, right with ╰.
    left_real5 = ROW_SLOTS[4][0][:5]
    right_real5 = ROW_SLOTS[4][1][2:]
    out.append(
        "//╰" + "┴".join(h for _ in left_real5) + "╯"
        + GAP
        + "╰" + "┴".join(h for _ in right_real5) + "╯"
    )

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

    # ── Line A: top 1u pairs ─────────────────────────────────────────────────
    # These sit above the 2u block on the right of the body.
    # Left pair (65, 66) aligns to body left slots 5-6 (inner).
    # Right pair (67, 68) aligns to body right slots 0-1 (inner).
    # Compute offset: left pair starts at col of body left-half slot 5.
    # slot 5 of left half → after boot banner, indented 2.
    # We use absolute spacing to match the body grid.
    # Left pair slot cols: 5*(w+3) and 6*(w+3); right pair: 0*(w+3) and 1*(w+3) in right half.
    # Half-width of 7 slots = 7*(w+3)-1 chars + "│" bookends for the cells.
    # Left half total with leading │ = 1 + 7*(w+3) chars.
    # The GAP is 6 chars.  Right half starts at: 2 + 7*(w+3) + 6 = 8 + 7*(w+3).
    # Token indent ("  " prefix) uses the same _binding_row slot math.

    # For the top 1u pair, we position them using body slot 5/6 (left) and 0/1 (right).
    # "  " + 5*(w+3) spaces + token65 + spaces + token66 + GAP + token67 + spaces + token68
    slot5_col = 5 * (w + 3)
    slot6_col = 6 * (w + 3)
    # Right half slot 0/1 (these correspond to slots 0 and 1 in the right half)
    # Right half starts at character 2 + 7*(w+3) + len(GAP) = 2 + 7*(w+3) + 6
    rbase = 7 * (w + 3) + len(GAP)

    # Border for line A
    out.append(
        "//" + " " * (slot5_col + 1)
        + "╭" + h + "┬" + h + "╮"
        + GAP
        + "╭" + h + "┬" + h + "╮"
    )

    # Bindings for line A (pos 65, 66 | 67, 68)
    half_w = 7 * (w + 3)
    lbuf = [" "] * half_w
    rbuf = [" "] * half_w
    for slot, pos in [(5, 65), (6, 66)]:
        tok = tokens[pos - 1]
        col = slot * (w + 3)
        for i, ch in enumerate(tok):
            if col + i < half_w:
                lbuf[col + i] = ch
    for slot, pos in [(0, 67), (1, 68)]:
        tok = tokens[pos - 1]
        col = slot * (w + 3)
        for i, ch in enumerate(tok):
            if col + i < half_w:
                rbuf[col + i] = ch
    out.append("  " + "".join(lbuf).rstrip() + GAP + "".join(rbuf).rstrip())

    # Labels for line A
    out.append(
        "//" + " " * (slot5_col + 1)
        + f"│ {lbl(65)} │ {lbl(66)} │"
        + GAP
        + f"│ {lbl(67)} │ {lbl(68)} │"
    )

    # ── Top border of 2u block ────────────────────────────────────────────────
    # Left side: opens at slot 3 (pos 69), extends through slot 4 (70), then slot 5 closes
    # into the inner 1u column (slot 5 stays part of line A's right edge).
    # The 3-cell left cluster: ╭─69─┼─70─┼─71─╮ at slots 3,4,5.
    # But slot 5 and 6 of the left body already belong to the line A pair.
    # The 2u block is an independent cluster BELOW the body.
    # Its left edge is at slot 3 of the left body half.
    slot3_col = 3 * (w + 3)

    out.append(
        "//" + " " * (slot3_col + 1)
        + "╭" + h + "┼" + h + "┼" + h + "┤"
        + GAP
        + "├" + h + "┼" + h + "┼" + h + "╮"
    )

    # Bindings for line B (pos 69, 70, 71 | 72, 73, 74)
    lbuf2 = [" "] * half_w
    rbuf2 = [" "] * half_w
    for slot, pos in [(3, 69), (4, 70), (5, 71)]:
        tok = tokens[pos - 1]
        col = slot * (w + 3)
        for i, ch in enumerate(tok):
            if col + i < half_w:
                lbuf2[col + i] = ch
    for slot, pos in [(0, 72), (1, 73), (2, 74)]:
        tok = tokens[pos - 1]
        col = slot * (w + 3)
        for i, ch in enumerate(tok):
            if col + i < half_w:
                rbuf2[col + i] = ch
    out.append("  " + "".join(lbuf2).rstrip() + GAP + "".join(rbuf2).rstrip())

    # First interior row of 2u block:
    # Left:  │ [69] label │ [70] label │ [71] label │   ← 71 label on top row
    # Right: │ [72] label │ [73] label │ [74] label │
    out.append(
        "//" + " " * (slot3_col + 1)
        + f"│ {lbl(69)} │ {lbl(70)} │ {lbl(71)} │"
        + GAP
        + f"│ {lbl(72)} │ {lbl(73)} │ {lbl(74)} │"
    )

    # Middle separator: 69/70/73/74 continue (blank), 71/72 split (inner 1u divider)
    out.append(
        "//" + " " * (slot3_col + 1)
        + f"│ {blank} │ {blank} ├" + h + "┤"
        + GAP
        + "├" + h + f"┤ {blank} │ {blank} │"
    )

    # Bindings for line C (pos 75 | 76) — slot 5 left, slot 0 right
    lbuf3 = [" "] * half_w
    rbuf3 = [" "] * half_w
    for slot, pos in [(5, 75)]:
        tok = tokens[pos - 1]
        col = slot * (w + 3)
        for i, ch in enumerate(tok):
            if col + i < half_w:
                lbuf3[col + i] = ch
    for slot, pos in [(0, 76)]:
        tok = tokens[pos - 1]
        col = slot * (w + 3)
        for i, ch in enumerate(tok):
            if col + i < half_w:
                rbuf3[col + i] = ch
    out.append("  " + "".join(lbuf3).rstrip() + GAP + "".join(rbuf3).rstrip())

    # Bottom interior row of 2u block: 69/70/73/74 blank, 71→75 / 72→76 labels
    out.append(
        "//" + " " * (slot3_col + 1)
        + f"│ {blank} │ {blank} │ {lbl(75)} │"
        + GAP
        + f"│ {lbl(76)} │ {blank} │ {blank} │"
    )

    # Bottom border
    out.append(
        "//" + " " * (slot3_col + 1)
        + "╰" + h + "┴" + h + "┴" + h + "╯"
        + GAP
        + "╰" + h + "┴" + h + "┴" + h + "╯"
    )

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
