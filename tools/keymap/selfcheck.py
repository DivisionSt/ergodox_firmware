"""Fast invariant checks for the keymap tooling. Run after editing either
firmware or the maps to confirm the parsers and position map still hold.

    python tools/keymap/selfcheck.py   # exits 0 on success
"""

from __future__ import annotations

from common import KEY_COUNT, load_layer_map, load_position_map
from parse_qmk import parse_qmk
from parse_zmk import parse_zmk
from translate import Category, equivalent


def main() -> int:
    failures: list[str] = []

    qmk = parse_qmk()
    zmk = parse_zmk()

    for idx, layer in qmk.items():
        if len(layer.keys) != KEY_COUNT:
            failures.append(f"QMK layer {idx} has {len(layer.keys)} keys (want {KEY_COUNT})")
    for idx, layer in zmk.items():
        if len(layer.keys) != KEY_COUNT:
            failures.append(f"ZMK layer {idx} has {len(layer.keys)} keys (want {KEY_COUNT})")

    pos_map = load_position_map()
    if sorted(pos_map.keys()) != list(range(1, KEY_COUNT + 1)):
        failures.append("position_map QMK side is not 1..76")
    if sorted(pos_map.values()) != list(range(1, KEY_COUNT + 1)):
        failures.append("position_map ZMK side is not a permutation of 1..76")

    # Layer map references must resolve to real layers.
    for pair in load_layer_map():
        if pair.qmk_index is not None and pair.qmk_index not in qmk:
            failures.append(f"layer_map references missing QMK layer {pair.qmk_index}")
        if pair.zmk_index is not None and pair.zmk_index not in zmk:
            failures.append(f"layer_map references missing ZMK layer {pair.zmk_index}")

    # Anchor: base-mac should align except the two known points.
    import translate
    from common import ZMK_KEYMAP
    from parse_zmk import parse_layer_defines
    translate.ZMK_LAYER_DEFINES = parse_layer_defines(ZMK_KEYMAP.read_text(encoding="utf-8"))
    qk, zk = qmk[0].keys, zmk[0].keys
    drift = [p for p in range(1, KEY_COUNT + 1)
             if equivalent(qk[p - 1], zk[pos_map[p] - 1]) is Category.DRIFT]
    if drift != [29]:
        failures.append(f"base-mac drift anchor changed: expected [29 (F24)], got {drift}")

    if failures:
        print("SELFCHECK FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("selfcheck OK: parsers, position map, layer map, and base-mac anchor all hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
