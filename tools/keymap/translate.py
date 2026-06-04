"""Translate QMK keycodes and ZMK bindings to a shared canonical form so the two
firmwares can be compared semantically rather than as raw strings.

`equivalent(qmk_token, zmk_token)` returns a Category describing how the two
sides relate at one key position.
"""

from __future__ import annotations

import re
from enum import Enum

from common import load_tsv, qmk_index_to_canonical, zmk_index_to_canonical

# --- Modifier aliases (intrinsic to the firmwares, stable) ------------------
# Canonical mod names are the QMK short forms.
_QMK_MOD = {
    "MOD_LSFT": "LSHFT", "MOD_LCTL": "LCTRL", "MOD_LALT": "LALT", "MOD_LGUI": "LGUI",
    "MOD_RSFT": "RSHFT", "MOD_RCTL": "RCTRL", "MOD_RALT": "RALT", "MOD_RGUI": "RGUI",
}
_ZMK_MOD = {
    "LSHFT": "LSHFT", "LCTRL": "LCTRL", "LALT": "LALT", "LGUI": "LGUI", "LCMD": "LGUI",
    "RSHFT": "RSHFT", "RCTRL": "RCTRL", "RALT": "RALT", "RGUI": "RGUI", "RCMD": "RGUI",
}
# Mod-wrapping functions (e.g. QMK LGUI(...), ZMK LG(...)).
_QMK_MODFN = {"LGUI": "LGUI", "LCTL": "LCTRL", "LALT": "LALT", "LSFT": "LSHFT",
              "RGUI": "RGUI", "RCTL": "RCTRL", "RALT": "RALT", "RSFT": "RSHFT"}
_ZMK_MODFN = {"LG": "LGUI", "LC": "LCTRL", "LA": "LALT", "LS": "LSHFT",
              "RG": "RGUI", "RC": "RCTRL", "RA": "RALT", "RS": "RSHFT"}

_BLANK = {"TRANS", "NONE"}


class Category(str, Enum):
    MATCH = "match"
    DRIFT = "drift"
    BLANK_DIFF = "blank-diff"   # both sides blank (trans vs none) but not identical
    UNMAPPED = "unmapped"        # a token could not be canonicalized on one/both sides


def _load_maps():
    atoms_z2q: dict[str, str] = {}
    tokens: dict[str, str] = {}      # qmk_token -> shared canonical
    tokens_z: dict[str, str] = {}    # zmk_token -> shared canonical
    for row in load_tsv("keycode_map.tsv"):
        if row["kind"] == "atom":
            atoms_z2q[row["zmk"]] = row["qmk"]
        elif row["kind"] == "token":
            canon = f"TOK::{row['qmk']}"
            tokens[row["qmk"]] = canon
            tokens_z[row["zmk"]] = canon
    return atoms_z2q, tokens, tokens_z


_ATOM_Z2Q, _TOKMAP_Q, _TOKMAP_Z = _load_maps()
_QMK_LAYER = qmk_index_to_canonical()
_ZMK_LAYER = zmk_index_to_canonical()

# Lazily filled: ZMK layer #define name -> index (set by parity at runtime).
ZMK_LAYER_DEFINES: dict[str, int] = {}


def _atom_qmk(raw: str) -> str:
    """Canonicalize a bare QMK atom (already KC_-stripped). Canonical == QMK form."""
    return raw


def _atom_zmk(raw: str) -> str:
    if raw in _ATOM_Z2Q:
        return _ATOM_Z2Q[raw]
    m = re.fullmatch(r"N([0-9])", raw)   # N1 -> 1
    if m:
        return m.group(1)
    return raw


def _modstack_qmk(token: str) -> tuple[str, bool] | None:
    mods: list[str] = []
    cur = token
    while True:
        m = re.fullmatch(r"([A-Z]+)\((.*)\)", cur)
        if not m or m.group(1) not in _QMK_MODFN:
            break
        mods.append(_QMK_MODFN[m.group(1)])
        cur = m.group(2)
    if not mods:
        return None
    inner = re.fullmatch(r"KC_(.+)", cur)
    if not inner:
        return f"??{token}", False
    return f"MODS({'+'.join(sorted(mods))},{_atom_qmk(inner.group(1))})", True


def _modstack_zmk(expr: str) -> tuple[str, bool] | None:
    mods: list[str] = []
    cur = expr
    while True:
        m = re.fullmatch(r"([A-Z]+)\((.*)\)", cur)
        if not m or m.group(1) not in _ZMK_MODFN:
            break
        mods.append(_ZMK_MODFN[m.group(1)])
        cur = m.group(2)
    if not mods:
        return None
    return f"MODS({'+'.join(sorted(mods))},{_atom_zmk(cur)})", True


def canon_qmk(token: str) -> tuple[str, bool]:
    token = token.strip()
    if token in _TOKMAP_Q:
        return _TOKMAP_Q[token], True
    if token == "KC_TRANSPARENT":
        return "TRANS", True
    if token == "KC_NO":
        return "NONE", True
    if token == "QK_LEAD":
        return "LEADER", True
    if token == "QK_REPEAT_KEY":
        return "REPEAT", True
    m = re.fullmatch(r"OSM\((MOD_[A-Z]+)\)", token)
    if m:
        return f"OSM({_QMK_MOD.get(m.group(1), m.group(1))})", True
    m = re.fullmatch(r"MT\((MOD_[A-Z]+),\s*KC_(.+)\)", token)
    if m:
        return f"MT({_QMK_MOD.get(m.group(1), m.group(1))},{_atom_qmk(m.group(2))})", True
    m = re.fullmatch(r"LT\((\d+),\s*KC_(.+)\)", token)
    if m:
        layer = _QMK_LAYER.get(int(m.group(1)), f"L{m.group(1)}")
        return f"LT({layer},{_atom_qmk(m.group(2))})", True
    m = re.fullmatch(r"(MO|TO|TG)\((\d+)\)", token)
    if m:
        layer = _QMK_LAYER.get(int(m.group(2)), f"L{m.group(2)}")
        return f"{m.group(1)}({layer})", True
    stack = _modstack_qmk(token)
    if stack is not None:
        return stack
    m = re.fullmatch(r"KC_(.+)", token)
    if m:
        return _atom_qmk(m.group(1)), True
    return f"??{token}", False


def _zmk_layer_canon(name: str) -> str:
    idx = ZMK_LAYER_DEFINES.get(name)
    if idx is not None and idx in _ZMK_LAYER:
        return _ZMK_LAYER[idx]
    return name


def canon_zmk(token: str) -> tuple[str, bool]:
    token = token.strip()
    if token in _TOKMAP_Z:
        return _TOKMAP_Z[token], True
    if token == "&trans":
        return "TRANS", True
    if token == "&none":
        return "NONE", True
    if token == "&leader":
        return "LEADER", True
    if token == "&key_repeat":
        return "REPEAT", True
    m = re.fullmatch(r"&sk (\w+)", token)
    if m:
        return f"OSM({_ZMK_MOD.get(m.group(1), m.group(1))})", True
    m = re.fullmatch(r"&t?mt (\w+) (\w+)", token)   # &mt / &tmt with simple mod
    if m and m.group(1) in _ZMK_MOD:
        return f"MT({_ZMK_MOD[m.group(1)]},{_atom_zmk(m.group(2))})", True
    m = re.fullmatch(r"&t?lt (L_[A-Z0-9_]+) (\w+)", token)   # &lt / &tlt layer-tap
    if m:
        return f"LT({_zmk_layer_canon(m.group(1))},{_atom_zmk(m.group(2))})", True
    m = re.fullmatch(r"&(to|mo|tog) (L_[A-Z0-9_]+)", token)
    if m:
        op = {"to": "TO", "mo": "MO", "tog": "TG"}[m.group(1)]
        return f"{op}({_zmk_layer_canon(m.group(2))})", True
    m = re.fullmatch(r"&kp (.+)", token)
    if m:
        stack = _modstack_zmk(m.group(1))
        if stack is not None:
            return stack
        return _atom_zmk(m.group(1)), True
    return f"??{token}", False


def equivalent(qmk_token: str, zmk_token: str) -> Category:
    qc, qok = canon_qmk(qmk_token)
    zc, zok = canon_zmk(zmk_token)
    if not qok or not zok:
        return Category.UNMAPPED
    if qc == zc:
        return Category.MATCH
    if qc in _BLANK and zc in _BLANK:
        return Category.BLANK_DIFF
    return Category.DRIFT
