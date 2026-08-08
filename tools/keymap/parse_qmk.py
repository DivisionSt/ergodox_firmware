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
# `const uint16_t PROGMEM comboN[] = { KC_A, KC_B, COMBO_END};`
_COMBO_DECL = re.compile(
    r"const\s+uint16_t\s+PROGMEM\s+(?P<name>\w+)\[\]\s*=\s*\{(?P<body>.*?)COMBO_END\s*\}\s*;",
    re.DOTALL,
)
# One arm of combo_should_trigger()'s switch, allowing stacked fall-through
# labels: `case A: case B: return <expr>;`
_TRIGGER_CASE = re.compile(
    r"(?P<labels>(?:case\s+[^:;]+:\s*)+)return\s+(?P<expr>[^;]+);", re.DOTALL
)
_CASE_LABEL = re.compile(r"case\s+([^:;]+):")


@dataclass
class QmkLayer:
    index: int
    name: str
    keys: list[str]  # length KEY_COUNT


@dataclass
class QmkCombo:
    index: int          # position in key_combos[]
    name: str           # the comboN array name
    triggers: list[str]  # QMK keycodes that must be chorded
    action: str          # the keycode the combo emits
    gate: str | None = None  # combo_should_trigger() expression, None == fires globally


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


def _norm(text: str) -> str:
    """Collapse whitespace so `LGUI(LSFT(KC_T))` and `LGUI( LSFT(KC_T) )` compare equal."""
    return "".join(text.split())


def _parse_combo_gates(source: str) -> dict[str, str]:
    """Map a combo's action keycode -> the `combo_should_trigger()` expression
    guarding it.

    The switch is keyed on `combo->keycode` rather than on the combo index, so
    the gates survive Oryx renumbering the combo table. Combos with no case arm
    fire on every layer and are simply absent here. The expression is captured
    verbatim rather than interpreted: the parity report shows it for context, it
    does not drive equivalence.
    """
    m = re.search(r"bool\s+combo_should_trigger\s*\(", source)
    if not m:
        return {}
    body = source[m.end() :]
    gates: dict[str, str] = {}
    for case in _TRIGGER_CASE.finditer(body):
        expr = " ".join(case.group("expr").split())
        for label in _CASE_LABEL.findall(case.group("labels")):
            gates[_norm(label)] = expr
    return gates


def parse_qmk_combos(path: Path = QMK_KEYMAP) -> list[QmkCombo]:
    """Parse the combo declarations and the key_combos[] table into QmkCombos.

    QMK combos are keyed by keycode rather than by physical position, so the
    triggers here are keycodes; parity.py resolves them to positions.
    """
    source = path.read_text(encoding="utf-8")
    triggers: dict[str, list[str]] = {}
    for m in _COMBO_DECL.finditer(source):
        body = re.sub(r"//[^\n]*", "", m.group("body"))
        triggers[m.group("name")] = [t for t in _split_top_level(body) if t]

    table = re.search(r"combo_t\s+key_combos\s*\[[^\]]*\]\s*=\s*\{", source)
    if not table:
        raise ValueError("no key_combos[] table found in the QMK keymap")
    gates = _parse_combo_gates(source)
    combos: list[QmkCombo] = []
    cursor = table.end()
    end = source.index("};", cursor)
    while True:
        entry = source.find("COMBO(", cursor)
        if entry == -1 or entry > end:
            break
        open_paren = source.index("(", entry)
        args = _split_top_level(_layer_body(source, open_paren))
        if len(args) != 2:
            raise ValueError(f"malformed COMBO() entry: {args}")
        name, action = args[0], args[1]
        if name not in triggers:
            raise ValueError(f"key_combos[] references undeclared combo array {name!r}")
        combos.append(
            QmkCombo(
                index=len(combos),
                name=name,
                triggers=triggers[name],
                action=action,
                gate=gates.get(_norm(action)),
            )
        )
        cursor = open_paren + 1
    return combos


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
    combos = parse_qmk_combos()
    print(f"Parsed {len(combos)} QMK combos")
    for combo in combos:
        gate = f"  gate={combo.gate}" if combo.gate else ""
        print(f"  [{combo.index:>2}] {combo.name:<8} {' + '.join(combo.triggers):<44}"
              f" -> {combo.action}{gate}")
