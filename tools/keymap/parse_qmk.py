"""Parse the QMK keymap (DYrAK/keymap.c) into per-layer keycode lists.

Each layer is a `[N] = LAYOUT_ergodox_pretty( // name ... )` block holding 76
comma-separated keycodes in flat "pretty" argument order. Keycodes may contain
nested parens (e.g. `LT(3, KC_BSPC)`, `LGUI(LCTL(KC_SPACE))`), so splitting is
paren-depth aware.

Run directly to print a summary:  python tools/keymap/parse_qmk.py
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from common import KEY_COUNT, QMK_KEYMAP

_LAYER_HEADER = re.compile(
    r"\[(?P<index>\d+)\]\s*=\s*LAYOUT_ergodox_pretty\(\s*(?://\s*(?P<name>[^\n]*))?"
)
# `#define NAME EXPANSION` for keymap aliases like DUAL_FUNC_0.
_DEFINE = re.compile(r"^#define\s+(?P<name>[A-Z0-9_]+)\s+(?P<body>.+?)\s*$", re.MULTILINE)


@dataclass
class QmkLayer:
    index: int
    name: str
    keys: list[str]  # length KEY_COUNT


def _split_top_level(text: str) -> list[str]:
    """Split on commas that sit at paren-depth 0."""
    tokens: list[str] = []
    depth = 0
    current = []
    for ch in text:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            tokens.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        tokens.append(tail)
    return tokens


def _layer_body(source: str, start: int) -> str:
    """Return the text inside the LAYOUT_ergodox_pretty(...) starting at `start`
    (the index of the opening paren), excluding the outer parens."""
    depth = 0
    for i in range(start, len(source)):
        if source[i] == "(":
            depth += 1
        elif source[i] == ")":
            depth -= 1
            if depth == 0:
                return source[start + 1 : i]
    raise ValueError("unbalanced parens in QMK layer body")


def parse_defines(source: str) -> dict[str, str]:
    return {m.group("name"): m.group("body").strip() for m in _DEFINE.finditer(source)}


def parse_qmk(path: Path = QMK_KEYMAP) -> dict[int, QmkLayer]:
    source = path.read_text(encoding="utf-8")
    layers: dict[int, QmkLayer] = {}
    for m in _LAYER_HEADER.finditer(source):
        index = int(m.group("index"))
        name = (m.group("name") or f"layer-{index}").strip()
        open_paren = source.index("(", m.start())
        body = _layer_body(source, open_paren)
        # Strip line comments inside the body.
        body = re.sub(r"//[^\n]*", "", body)
        keys = _split_top_level(body)
        if len(keys) != KEY_COUNT:
            raise ValueError(
                f"QMK layer [{index}] {name}: expected {KEY_COUNT} keys, got {len(keys)}"
            )
        layers[index] = QmkLayer(index=index, name=name, keys=keys)
    return layers


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    parsed = parse_qmk()
    print(f"Parsed {len(parsed)} QMK layers from {QMK_KEYMAP.name}")
    for idx, layer in parsed.items():
        print(f"  [{idx}] {layer.name:<10} {len(layer.keys)} keys")
