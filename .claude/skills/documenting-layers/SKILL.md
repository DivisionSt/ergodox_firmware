---
name: documenting-layers
description: Generates or refreshes LAYERS.md, the human-readable map of every Ergodox layer, from the ZMK keymap (the home-keyboard superset) with QMK coverage and per-layer drift marked. Use when the user asks to document the layout, update LAYERS.md, or after layers/keys change in either firmware.
---

# Documenting layers

`LAYERS.md` at the repo root is a generated reference: every ZMK layer rendered
as a key grid, with an at-a-glance table marking which layers QMK also carries
and where the two firmwares diverge. ZMK is the source of truth because it is
the superset (home keyboard); QMK is a subset of it.

## Regenerate

```bash
python3 tools/keymap/layers.py --write   # writes LAYERS.md at repo root
python3 tools/keymap/layers.py           # print to stdout (preview only)
```

That is the whole job for a routine refresh. `LAYERS.md` is generated — do not
hand-edit it; change the source keymaps (or the layer purposes / display labels
in `tools/keymap/layers.py`) and regenerate.

## What it reads

- `config/slicemk_ergodox.keymap` — every layer's bindings (the superset).
- `tools/keymap/maps/layer_map.tsv` — QMK↔ZMK layer correspondence and which
  layers are intentionally home-only.
- The parity engine (`tools/keymap/parity.py`) — to annotate each overlapping
  layer with the keys where QMK differs.

## When the output looks wrong

- A new layer shows no purpose text → add its canonical slug to the `PURPOSE`
  dict in `tools/keymap/layers.py`.
- A binding renders as raw text (e.g. `bt BT_SEL 0`) → extend `display()` in
  `tools/keymap/layers.py` with a label for that behavior.
- A layer is missing or mislabeled → check `tools/keymap/maps/layer_map.tsv`.

After regenerating, run `python3 tools/keymap/selfcheck.py` to confirm the
parsers still agree with the source.
