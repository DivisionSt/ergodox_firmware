---
name: syncing-qmk-zmk
description: Compares the QMK layout (DYrAK/keymap.c, the work keyboard) and the ZMK layout (config/slicemk_ergodox.keymap, the home keyboard) layer-by-layer and reports keycode drift, treating ZMK-only layers as intentional. Use when checking layout parity between QMK and ZMK, after editing either firmware, or when the user asks to sync, diff, or reconcile the two keymaps.
---

# Syncing QMK and ZMK

This repo keeps one Ergodox layout in two firmwares. QMK (`DYrAK/`) is the work
keyboard and carries only the shared base/extend layers. ZMK (`config/`) is the
home keyboard and is a deliberate **superset** with extra game/app base layers
(fortnite, minecraft, gaming, sketchup) plus underglow. Those ZMK-only layers
are **not drift** — only the overlapping layers should agree.

The two firmwares spell the same key differently (`KC_ESCAPE` vs `&kp ESC`,
`LT(3,KC_BSPC)` vs `&tlt L_EXT_NAV BSPC`), so this is a **semantic** comparison,
not a string diff. The physical thumb cluster is also ordered differently
between QMK's `LAYOUT_ergodox_pretty` and ZMK's matrix transform; the position
map handles that.

## Quick start

Run the parity report from the repo root:

```bash
python3 tools/keymap/parity.py            # full report with per-key diffs
python3 tools/keymap/parity.py --summary  # counts per layer only
python3 tools/keymap/parity.py --layer mac
```

Exit code is non-zero when real drift or unmapped tokens exist. Each non-matching
key is classified:

- **DRIFT** — a genuine keycode difference between the two firmwares. Surface
  these; the user decides which side is canonical for that key.
- **UNMAPPED** — a token the translator couldn't canonicalize (usually a QMK
  custom keycode like `LAYER_ID`, or a firmware-specific binding like `&bt`).
  Either it has no counterpart, or the maps need a new entry.
- **blank-diff** — one side `KC_TRANSPARENT`, the other `&none`. Informational
  (hidden by default in the report); meaningful only on non-base layers.

## How to use the output

1. Run `--summary` first to see which layers diverge.
2. For a flagged layer, run `--layer <slug>` and read the per-key diffs.
3. For each DRIFT, confirm with the user which firmware is correct, then edit the
   losing side's source file directly. Do **not** auto-resolve.
4. For each UNMAPPED that is a real equivalence (not a true divergence), add a
   row to `tools/keymap/maps/keycode_map.tsv` (see below) and re-run.
5. After any edit, run `python3 tools/keymap/selfcheck.py` to confirm the
   parsers and maps still hold.

Layer slugs: `mac win old nav num wnav wnum func mouse layers`. Expect real
divergence on `layers` and `mouse` — those hold firmware-specific utility keys
(ZMK Bluetooth/output management, ZMK mouse behaviors) that QMK has no analog
for. The base and extend layers are the meaningful parity targets.

## The maps (when to edit which)

All under `tools/keymap/maps/`:

- **`keycode_map.tsv`** — QMK⇄ZMK equivalences. Add an `atom` row when a plain
  keycode spells differently (`ENTER`⇄`RET`); add a `token` row for a custom
  behavior with no structural match (`&cmd_tab`, `&mmv MOVE_LEFT`). This is the
  file you edit most as the layout grows.
- **`layer_map.tsv`** — which QMK layer maps to which ZMK layer, and which ZMK
  layers are intentionally home-only. Edit when you add or reindex a layer.
- **`position_map.tsv`** — physical key correspondence (QMK pretty-arg order ⇄
  ZMK matrix order). Rows 1-64 are identity; 65-76 are the thumb permutation.
  Rarely changes — only if the hardware/matrix changes.

## Build reality

This is **static analysis** of committed source. It does not compile or flash.
Firmware is built only in CI (QMK via the `fetch-and-build-layout` Action, ZMK
via the upstream Action). Never report a synced change as "verified working" —
that requires the user's CI build and a flash.
