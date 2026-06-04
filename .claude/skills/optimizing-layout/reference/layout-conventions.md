# Layout conventions

How the DivisionSt Ergodox layout works. The **mechanics** below are read from
the firmware (`DYrAK/keymap.c`, `config/slicemk_ergodox.keymap`) and are
authoritative. The **intent** notes marked _(confirm with Forrest)_ are
inferences — replace them with his actual reasoning as it comes up, and add new
preferences here whenever he explains or rejects something.

## Firmware split

- **QMK (`DYrAK/`)** — work keyboard. Base layers + extends only (10 layers).
- **ZMK (`config/`)** — home keyboard, the superset (16 layers): adds game/app
  bases (fortnite, minecraft, gaming, sketchup) and underglow. Intentional.

## Base layers

- `base-mac` (0) is the default. `base-win` (1/ZMK 4) mirrors it with Ctrl-based
  shortcuts where mac uses Cmd. `base-old` (2/ZMK 6) is a legacy fallback.
- Alpha home row is plain letters (no home-row mods on base). Mods come via
  one-shot keys and the extend layers instead. _(confirm with Forrest: deliberate
  choice to avoid HRM timing on the base?)_
- `chordal_hold_layout` is defined (chordal/achordion-style hold handling).

## Thumbs (the workhorses)

Per `base-mac`:
- Left: leader · dual-function (tap ⏯ / hold mission-control) · vol+ ·
  **LT(nav)/Backspace** · one-shot Cmd · vol-.
- Right: **TO(layers)** · repeat · (layer-id / none) · trans · **Cmd/Enter
  mod-tap** · **LT(num)/Space**.
- Layer access lives on the big thumb keys: hold Backspace → nav, hold Space →
  num. Windows variants use LT(5)/LT(6).
- `LT(_, SPACE)` tapping term is bumped +40ms to reduce space misfires.

## One-shot mods

Extend-layer left home row is `OSM(SHIFT/CTRL/ALT/GUI)` (ZMK `&sk`). Sticky mods
rather than held mods for layered chording.

## Combos (11)

- Thumb-pair toggles: nav/num/func/win-nav/win-num layer `TG`/`tog` via
  combining the two thumb layer keys or a thumb + mod.
- App/window shortcuts: adjacent-key combos fire Cmd+Shift+{T,V,A,L} and
  Ctrl/Alt chords. Watch fast-roll false triggers on the alpha combos (Q+W, Z+X,
  B+V).

## Leader key (QMK `leader_end_user`)

A large tree, mac-oriented:
- Single: `t`/`v`/`a` → Cmd+Shift+{T,V,A}.
- `/ i` → speak current layer name.
- `r …` → **Rectangle** window manager (halves, thirds, quarters, maximize,
  displays). Mnemonics: `r w o/m/c` = window thirds, `r h o/m/c` = ..., `r 1/2/3`
  = positions.
- `d …` → desktop / window navigation (spaces, fullscreen).
- `s …` → app shortcuts.

## Utility layers

- `mouse` (8/ZMK 12) — mouse move/scroll/clicks. ZMK uses native `&mmv/&msc/&mkp`.
- `layers` (9/ZMK 13) — layer switching + config. QMK exposes dynamic-tapping-term
  tuning keys; ZMK exposes Bluetooth/output/reset (wireless-only). This layer is
  expected to diverge between the firmwares.

## Known intentional divergences (not drift)

- ZMK-only base layers: fortnite, minecraft, gaming, sketchup (home gaming/CAD).
- `base-mac` `KC_F24` (left home pinky) has no ZMK counterpart _(confirm: leftover
  or intentional?)_.
- `LAYER_ID` (QMK speak-layer-name) is QMK-only.
- `mouse`/`layers` utility keys differ by firmware capability.

## Open questions for Forrest

- Is `KC_F24` on base-mac still used, or vestigial?
- Should any home-only ZMK layer ever come to QMK, or is the split permanent?
- Preferred tapping-term feel (currently `g_tapping_term`, +40ms on space)?
