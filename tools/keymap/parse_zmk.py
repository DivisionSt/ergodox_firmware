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
# A `combo_name { ... };` node inside the `combos { ... }` block.
_COMBO_NODE = re.compile(r"(?P<name>\w+)\s*\{(?P<body>[^{}]*?)\}\s*;", re.DOTALL)
_COMBO_PROP = re.compile(r"(?P<key>[\w-]+)\s*=\s*<(?P<value>[^>]*)>\s*;")


@dataclass
class ZmkLayer:
    index: int
    name: str
    bindings: list[str]  # length KEY_COUNT + 1 (index 0 = bootloader/trans slot)

    @property
    def keys(self) -> list[str]:
        """Physical positions 1..76 (drops the slot-0 bootloader/trans)."""
        return self.bindings[1:]


@dataclass
class ZmkCombo:
    name: str
    key_positions: list[int]  # physical positions 1..76 (== binding index)
    binding: str              # the behaviour the combo fires
    layers: list[str]         # L_* names the combo is restricted to


def parse_layer_defines(source: str) -> dict[str, int]:
    """Map `#define L_EXT_NAV 7` names to their layer index."""
    return {m.group("name"): int(m.group("index")) for m in _DEFINE_LAYER.finditer(source)}


def parse_zmk_combos(path: Path = ZMK_KEYMAP) -> list[ZmkCombo]:
    """Parse the `combos { ... }` node into ZmkCombos.

    ZMK combo `key-positions` are keymap binding indices, which line up exactly
    with the physical positions used elsewhere in this tooling (binding index 0
    is the bootloader slot, so index N is physical position N).
    """
    source = path.read_text(encoding="utf-8")
    start = re.search(r"combos\s*\{", source)
    if not start:
        return []
    # Walk to the matching brace so sibling nodes are not swept in.
    depth = 0
    for i in range(start.end() - 1, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                block = source[start.end() : i]
                break
    else:
        raise ValueError("unbalanced braces in ZMK combos block")

    block = "\n".join(
        line for line in block.splitlines() if not line.lstrip().startswith("//")
    )
    combos: list[ZmkCombo] = []
    for node in _COMBO_NODE.finditer(block):
        props = {p.group("key"): p.group("value").strip()
                 for p in _COMBO_PROP.finditer(node.group("body"))}
        if "key-positions" not in props or "bindings" not in props:
            continue
        positions = [int(v) for v in props["key-positions"].split()]
        binding = " ".join(props["bindings"].split())
        layers = props.get("layers", "").split()
        combos.append(
            ZmkCombo(
                name=node.group("name"),
                key_positions=positions,
                binding=binding,
                layers=layers,
            )
        )
    return combos


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
    combos = parse_zmk_combos()
    print(f"Parsed {len(combos)} ZMK combos")
    for combo in combos:
        positions = "+".join(str(p) for p in combo.key_positions)
        print(f"  {combo.name:<26} {positions:<8} -> {combo.binding:<20}"
              f" layers={','.join(combo.layers) or 'all'}")
