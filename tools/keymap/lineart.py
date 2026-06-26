"""Regenerate the ASCII lineart comment blocks in config/slicemk_ergodox.keymap.

The lineart is the box-drawing // comments above each layer's bindings that
visually depict the keyboard layout. They drift from the real bindings because
nothing previously generated or checked them. This script fixes that.

    python3 tools/keymap/lineart.py           # dry run: print unified diff
    python3 tools/keymap/lineart.py --write   # rewrite the keymap in place
    python3 tools/keymap/lineart.py --check   # exit 1 if regen would change file

Design:
- Binding tokens are re-emitted VERBATIM (only surrounding whitespace changes).
  The script never alters token content — only comments and whitespace.
- Cell labels: "[N] LABEL" where N is the 1-indexed physical position and LABEL
  comes from lineart_labels.tsv (human overrides) with layers.display() as fallback.
- Cell width: auto-sized per layer to the longest label in that layer.
- Dead cells removed: home row 6|6, bottom row 5|5 (matching the physical keyboard).
- 2u thumb keys (ZMK pos 69/70 left, 73/74 right) render as taller 3-row cells
  with the label vertically centered; the inner 1u column stacks beside them.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

# Allow running from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import KEY_COUNT, MAPS_DIR, ZMK_KEYMAP, load_tsv
from layers import display
from parse_zmk import parse_zmk

# ── Physical geometry ─────────────────────────────────────────────────────────
# Each entry is (left_positions, right_positions) for a main-body row.
ROWS = [
    (range(1, 8),   range(8, 15)),   # row 1: 7|7
    (range(15, 22), range(22, 29)),  # row 2: 7|7
    (range(29, 35), range(35, 41)),  # row 3 home: 6|6
    (range(41, 48), range(48, 55)),  # row 4: 7|7
    (range(55, 60), range(60, 65)),  # row 5 bottom: 5|5
]

# Thumb cluster positions. The 2u keys are 69/70 (left) and 73/74 (right).
# Layout (three source binding lines):
#   line A: 65 66  |  67 68        (top 1u pairs)
#   line B: 69 70 71 | 72 73 74   (left: 2u 2u 1u; right: 1u 2u 2u)
#   line C: 75      |  76          (inner 1u singles)

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


# ── Cell label (with position prefix) ────────────────────────────────────────
def _cell_label(pos: int, token: str) -> str:
    """Return '[N] LABEL' for a regular key cell."""
    return f"[{pos}] {_label(token)}"


def _boot_label(token: str) -> str:
    return _label(token)


# ── Box-drawing helpers ───────────────────────────────────────────────────────
def _pad(text: str, width: int) -> str:
    """Center text within width, space-padded."""
    return text[:width].center(width)


def _hbar(width: int) -> str:
    return "─" * width


def _top_border(widths: list[int]) -> str:
    return "╭" + "┬".join(_hbar(w + 2) for w in widths) + "╮"


def _mid_border(widths: list[int]) -> str:
    return "├" + "┼".join(_hbar(w + 2) for w in widths) + "┤"


def _bot_border(widths: list[int]) -> str:
    return "╰" + "┴".join(_hbar(w + 2) for w in widths) + "╯"


def _row_line(labels: list[str], widths: list[int]) -> str:
    cells = "│".join(f" {_pad(lbl, w)} " for lbl, w in zip(labels, widths))
    return "│" + cells + "│"


def _top_border_open_right(left_widths: list[int], gap: int, right_widths: list[int]) -> str:
    """Top border that opens (╭) on left, has a gap, and opens (╭) on right."""
    left = "╭" + "┬".join(_hbar(w + 2) for w in left_widths) + "┐"
    right = "╭" + "┬".join(_hbar(w + 2) for w in right_widths) + "┐"
    return left + " " * gap + right


def _mid_border_open_right(left_widths: list[int], gap: int, right_widths: list[int]) -> str:
    left = "├" + "┼".join(_hbar(w + 2) for w in left_widths) + "┤"
    right = "├" + "┼".join(_hbar(w + 2) for w in right_widths) + "┤"
    return left + " " * gap + right


def _bot_border_open_right(left_widths: list[int], gap: int, right_widths: list[int]) -> str:
    left = "╰" + "┴".join(_hbar(w + 2) for w in left_widths) + "╯"
    right = "╰" + "┴".join(_hbar(w + 2) for w in right_widths) + "╯"
    return left + " " * gap + right


def _row_line_two_halves(
    left_labels: list[str], left_widths: list[int],
    gap: int,
    right_labels: list[str], right_widths: list[int],
) -> str:
    left = "│" + "│".join(f" {_pad(l, w)} " for l, w in zip(left_labels, left_widths)) + "│"
    right = "│" + "│".join(f" {_pad(l, w)} " for l, w in zip(right_labels, right_widths)) + "│"
    return left + " " * gap + right


# ── Compute cell width for a layer ────────────────────────────────────────────
def _max_label_len(tokens: list[str], positions: list[int]) -> int:
    """Max length of [N] LABEL across given positions (1-indexed)."""
    return max(len(_cell_label(p, tokens[p - 1])) for p in positions)


def _layer_cell_width(tokens: list[str]) -> int:
    """Uniform cell width for all keys of a layer (body + thumbs)."""
    return max(len(_cell_label(p, tokens[p - 1])) for p in range(1, KEY_COUNT + 1))


# ── Render the bootloader banner ──────────────────────────────────────────────
def _render_boot_banner(boot_token: str, body_width: int) -> list[str]:
    """Full-width banner for the bootloader (slot 0)."""
    label = _boot_label(boot_token)
    inner = body_width - 2  # subtract the ╭╮
    lines = []
    lines.append(f"//╭{'─' * inner}╮")
    lines.append(f"  {boot_token}")
    lines.append(f"//│ {label.ljust(inner - 2)} │")
    return lines


# ── Render five main body rows ────────────────────────────────────────────────
GAP = "      "  # 6 spaces between left and right halves in the lineart


def _render_main_rows(tokens: list[str], w: int) -> list[str]:
    """
    Render the 5 main rows. Each row: binding line + lineart comment line.
    Row 3 (home, 6|6) and row 5 (bottom, 5|5) have no inner gap cells.
    Rows 1, 2, 4 are 7|7 with the full gap between halves.
    """
    lines = []

    def bindings_line(positions: list[int]) -> str:
        return "  " + "  ".join(tokens[p - 1] for p in positions)

    def label_line(positions: list[int], widths: list[int]) -> str:
        labels = [_cell_label(p, tokens[p - 1]) for p in positions]
        return "//│" + "│".join(f" {_pad(l, wd)} " for l, wd in zip(labels, widths)) + "│"

    for row_idx, (left, right) in enumerate(ROWS):
        lp = list(left)
        rp = list(right)
        lw = [w] * len(lp)
        rw = [w] * len(rp)

        if row_idx == 0:
            # First row: top border for left + right
            lines.append("//├" + "┬".join(_hbar(w + 2) for _ in lp) + "┐" +
                          f"      ╭" + "┬".join(_hbar(w + 2) for _ in rp) + "┐")
        else:
            lines.append("//├" + "┼".join(_hbar(w + 2) for _ in lp) + "┤" +
                          f"      ├" + "┼".join(_hbar(w + 2) for _ in rp) + "┤")

        # binding row
        lines.append("  " + "  ".join(tokens[p - 1] for p in lp) +
                      "      " +
                      "  ".join(tokens[p - 1] for p in rp))
        # label row
        lines.append("//│" + "│".join(f" {_pad(_cell_label(p, tokens[p-1]), w)} " for p in lp) + "│" +
                      "      " +
                      "│" + "│".join(f" {_pad(_cell_label(p, tokens[p-1]), w)} " for p in rp) + "│")

    # bottom border of row 5 transitions into thumb area
    lp5 = list(ROWS[4][0])
    rp5 = list(ROWS[4][1])
    lines.append("//╰" + "┴".join(_hbar(w + 2) for _ in lp5) + "┴".join(["─" * (w + 2)] * 0) +
                 _hbar(w + 2) + "╯" +
                 "      " +
                 "╰" + "┴".join(_hbar(w + 2) for _ in rp5) + "┴".join(["─" * (w + 2)] * 0) +
                 _hbar(w + 2) + "╯")

    return lines


def _render_main_rows_v2(tokens: list[str], w: int) -> list[str]:
    """
    Correct rendering of 5 main rows with proper borders.
    Returns lines that are COMMENTS ONLY (//...) interleaved with binding lines.
    The caller will prefix binding lines with the right indent.
    """
    lines = []

    def lbar(n): return "┬".join(_hbar(w + 2) for _ in range(n))
    def mbar(n): return "┼".join(_hbar(w + 2) for _ in range(n))
    def bbar(n): return "┴".join(_hbar(w + 2) for _ in range(n))

    for row_idx, (left, right) in enumerate(ROWS):
        lp = list(left)
        rp = list(right)

        # top/mid border for this row
        if row_idx == 0:
            b_left  = "//├" + lbar(len(lp)) + "┐"
            b_right = "╭"   + lbar(len(rp)) + "┐"
        else:
            b_left  = "//├" + mbar(len(lp)) + "┤"
            b_right = "├"   + mbar(len(rp)) + "┤"
        lines.append(b_left + GAP + b_right)

        # binding row (actual code)
        bind = "  " + "  ".join(tokens[p - 1] for p in lp) + GAP + "  ".join(tokens[p - 1] for p in rp)
        lines.append(bind)

        # label comment row
        def lbl(p): return _pad(_cell_label(p, tokens[p - 1]), w)
        lcells = "│".join(f" {lbl(p)} " for p in lp)
        rcells = "│".join(f" {lbl(p)} " for p in rp)
        lines.append("//│" + lcells + "│" + GAP + "│" + rcells + "│")

    # bottom border after row 5
    lp5 = list(ROWS[4][0])
    rp5 = list(ROWS[4][1])
    lines.append("//╰" + bbar(len(lp5)) + "╯" + GAP + "╰" + bbar(len(rp5)) + "╯")

    return lines


# ── Render thumb cluster ──────────────────────────────────────────────────────
def _render_thumbs(tokens: list[str], w: int) -> list[str]:
    """
    Thumb cluster. Positions:
      line A (top 1u pairs):   65 66 |gap| 67 68
      line B (2u + 1u col):    69(2u) 70(2u) 71(1u) |gap| 72(1u) 73(2u) 74(2u)
      line C (inner singles):  75 |gap| 76

    2u keys span 3 interior rows; inner 1u column (71/75, 72/76) beside them.
    Layout mirrors the approved "taller, label centered" preview:

      Left side:                          Right side:
      ╭──────┬──────╮                     ╭──────┬──────╮
      │  65  │  66  │                     │  67  │  68  │
      ├──────┼──────┼──────╮              ╭──────┼──────┼──────┤
      │      │      │  71  │              │  72  │      │      │
      │  69  │  70  ├──────┤              ├──────┤  73  │  74  │
      │ (2u) │ (2u) │  75  │              │  76  │ (2u) │ (2u) │
      ╰──────┴──────┴──────╯              ╰──────┴──────┴──────╯
    """
    lines = []

    def lbl(p): return _pad(_cell_label(p, tokens[p - 1]), w)
    def h(): return _hbar(w + 2)

    # ── Line A: top 1u pairs ──────────────────────────────────────────────────
    # Border
    lines.append(f"//                                             ╭{h()}┬{h()}╮      ╭{h()}┬{h()}╮")
    # Bindings
    lines.append(f"                                               {tokens[64]}  {tokens[65]}      {tokens[66]}  {tokens[67]}")
    # Labels
    lines.append(f"//                                             │ {lbl(65)} │ {lbl(66)} │      │ {lbl(67)} │ {lbl(68)} │")

    # ── Line B: 2u pair + inner 1u, top boundary ──────────────────────────────
    # Left side opens 3-wide (69, 70, 71), right side opens 3-wide (72, 73, 74)
    lines.append(f"//                              ╭{h()}┼{h()}┼{h()}┤      ├{h()}┼{h()}┼{h()}╮")
    # Bindings (69 70 71 | 72 73 74): row B
    lines.append(f"                                {tokens[68]}  {tokens[69]}  {tokens[70]}      {tokens[71]}  {tokens[72]}  {tokens[73]}")
    # Top of 2u cells: label on top row, empty on middle+bottom rows for 2u
    # For 2u (69, 70, 73, 74): emit label on first interior row, blank on next two
    # For 1u (71, 72): emit label then separator
    lines.append(f"//                              │ {lbl(69)} │ {lbl(70)} │ {lbl(71)} │      │ {lbl(72)} │ {lbl(73)} │ {lbl(74)} │")

    # Middle row of 2u (blank label rows for 69/70/73/74, separator for 71/72)
    blank = _pad("", w)
    lines.append(f"//                              │ {blank} │ {blank} ├{h()}┤      ├{h()}┤ {blank} │ {blank} │")
    # Bindings for line C (75 | 76)
    lines.append(f"                                               {tokens[74]}      {tokens[75]}")
    # Bottom row of 2u (still 69/70/73/74), plus label for 71/75 and 72/76
    lines.append(f"//                              │ {blank} │ {blank} │ {lbl(75)} │      │ {lbl(76)} │ {blank} │ {blank} │")

    # Bottom border
    lines.append(f"//                              ╰{h()}┴{h()}┴{h()}╯      ╰{h()}┴{h()}┴{h()}╯")

    return lines


# ── Assemble the full lineart for one layer ───────────────────────────────────
BOOT_BANNER_WIDTH = 80  # width of the ╭...╮ boot banner


def render_layer(index: int, name: str, boot_token: str, tokens: list[str]) -> list[str]:
    """
    Returns the complete lines that replace 'bindings = <' ... '>;' contents.
    Lines alternate: binding tokens (code) and // comment rows (lineart).
    The caller will splice them back into the file preserving indentation.
    """
    w = _layer_cell_width(tokens)

    out: list[str] = []

    # Boot banner
    inner = BOOT_BANNER_WIDTH - 2
    out.append(f"//╭{'─' * inner}╮")
    out.append(f"  {boot_token}")
    out.append(f"//│ {_boot_label(boot_token).ljust(inner - 2)} │")

    # Main body rows
    out.extend(_render_main_rows_v2(tokens, w))

    # Thumb cluster
    out.extend(_render_thumbs(tokens, w))

    return out


# ── Parse the source and splice in regenerated blocks ────────────────────────
_LAYER_RE = re.compile(
    r"(layer_\d+\s*\{[^{]*?bindings\s*=\s*<)(.*?)(>\s*;)",
    re.DOTALL,
)


def _generate(source: str) -> str:
    """Return full rewritten source with regenerated lineart blocks."""
    zmk = parse_zmk()

    def replace_block(m: re.Match) -> str:
        prefix = m.group(1)   # 'layer_N { ... bindings = <'
        suffix = m.group(3)   # '>;\n'

        # Identify which layer this is by finding the layer index in prefix
        lm = re.search(r"layer_(\d+)", prefix)
        if not lm:
            return m.group(0)
        idx = int(lm.group(1))
        if idx not in zmk:
            return m.group(0)

        layer = zmk[idx]
        boot_token = layer.bindings[0]
        tokens = layer.keys  # 76 entries, 0-indexed = pos-1

        rendered = render_layer(idx, layer.name, boot_token, tokens)
        inner = "\n" + "\n".join(rendered) + "\n\t\t\t"
        return prefix + inner + suffix

    return _LAYER_RE.sub(replace_block, source)


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="rewrite keymap in place")
    ap.add_argument("--check", action="store_true", help="exit 1 if regen would change file")
    ap.add_argument("--path", type=Path, default=ZMK_KEYMAP, help="keymap file (default: ZMK_KEYMAP)")
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

    # Default: unified diff
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
