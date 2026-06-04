"""Parse the ZMK keymap (config/slicemk_ergodox.keymap) into per-layer binding
lists.

Each layer is a `layer_N { // name ... bindings = < ... >; }` block. Bindings
are `&`-prefixed tokens (`&kp ESC`, `&mt LC(LG(Q)) C_PP`, `&tlt L_EXT_NAV BSPC`)
interspersed with `//` comment lines. Binding index 0 is the bootloader/trans
slot; physical positions are 1..76.

Run directly to print a summary:  python tools/keymap/parse_zmk.py
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from common import KEY_COUNT, ZMK_KEYMAP

_LAYER_HEADER = re.compile(r"layer_(?P<index>\d+)\s*\{\s*//\s*(?P<name>[^\n]*)")
_DEFINE_LAYER = re.compile(r"^#define\s+(?P<name>L_[A-Z0-9_]+)\s+(?P<index>\d+)", re.MULTILINE)


@dataclass
class ZmkLayer:
    index: int
    name: str
    bindings: list[str]  # length KEY_COUNT + 1 (index 0 = bootloader/trans slot)

    @property
    def keys(self) -> list[str]:
        """Physical positions 1..76 (drops the slot-0 bootloader/trans)."""
        return self.bindings[1:]


def parse_layer_defines(source: str) -> dict[str, int]:
    """Map `#define L_EXT_NAV 7` names to their layer index."""
    return {m.group("name"): int(m.group("index")) for m in _DEFINE_LAYER.finditer(source)}


def _tokenize_bindings(block: str) -> list[str]:
    # Drop comment lines, then split on '&'. No binding contains '&'.
    no_comments = "\n".join(
        line for line in block.splitlines() if not line.lstrip().startswith("//")
    )
    parts = no_comments.split("&")
    tokens = []
    for part in parts[1:]:  # parts[0] is whitespace before the first '&'
        token = "&" + " ".join(part.split())
        tokens.append(token.strip())
    return tokens


def parse_zmk(path: Path = ZMK_KEYMAP) -> dict[int, ZmkLayer]:
    source = path.read_text(encoding="utf-8")
    layers: dict[int, ZmkLayer] = {}
    for m in _LAYER_HEADER.finditer(source):
        index = int(m.group("index"))
        name = m.group("name").strip()
        b_start = source.index("bindings = <", m.start())
        b_open = source.index("<", b_start)
        b_close = source.index(">", b_open)
        bindings = _tokenize_bindings(source[b_open + 1 : b_close])
        if len(bindings) != KEY_COUNT + 1:
            raise ValueError(
                f"ZMK layer_{index} {name}: expected {KEY_COUNT + 1} bindings "
                f"(incl. slot 0), got {len(bindings)}"
            )
        layers[index] = ZmkLayer(index=index, name=name, bindings=bindings)
    return layers


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    parsed = parse_zmk()
    print(f"Parsed {len(parsed)} ZMK layers from {ZMK_KEYMAP.name}")
    for idx, layer in parsed.items():
        print(f"  layer_{idx:<2} {layer.name:<22} {len(layer.keys)} keys (+slot0)")
