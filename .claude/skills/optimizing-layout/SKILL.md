---
name: optimizing-layout
description: Analyzes the Ergodox layout for ergonomic improvements — home-row/one-shot mods, combos, leader sequences, layer access, and thumb usage — and proposes changes with tradeoffs for the user to decide. Use when the user asks to optimize, evolve, critique, or rethink the keyboard layout, or to add a new key/combo/leader sequence.
---

# Optimizing the layout

This skill helps evolve the layout as the user's usage drifts. It is **advisory**:
propose options with tradeoffs and let the user decide. Layout is muscle memory —
never "improve" it unprompted, and never apply changes without explicit sign-off.

Read `reference/layout-conventions.md` first — it captures how this layout
actually works (the mechanisms and the user's intent) so proposals fit the
system instead of fighting it.

## Approach

1. **Ground in the current layout.** Run `python3 tools/keymap/parity.py
   --summary` and skim `LAYERS.md` so proposals reference real positions.
2. **Anchor to a real problem.** Optimize against a stated friction (a reach
   that hurts, a combo that misfires, a missing shortcut) — not abstract
   "cleanliness." If the user hasn't named one, ask what's bugging them.
3. **Propose, with tradeoffs.** For each idea give: what changes, which
   layer(s)/position(s), the upside, the cost (muscle-memory relearn, conflict
   risk, parity impact), and a confidence level.
4. **Respect the QMK/ZMK split.** QMK is the work keyboard (base layers only);
   ZMK is the home superset. A change to a shared layer must land in both or be
   a deliberate divergence — flag which. Use the `syncing-qmk-zmk` skill to check.
5. **Hand off the edit.** When the user picks a change, edit the source files
   (`DYrAK/keymap.c` and/or `config/slicemk_ergodox.keymap`), then run
   `syncing-qmk-zmk` and offer `updating-kle` + `documenting-layers` to keep the
   KLE and `LAYERS.md` in step.

## What to look at

- **Thumb load** — the thumbs carry layer access (`LT`/`tlt`), enter, space,
  mods. Overloading them causes misfires; underusing them wastes the best keys.
- **One-shot mods (OSM/`&sk`)** — used on extend-layer home rows. Check for
  timing friction and double-tap-lock needs.
- **Combos** — 11 today (layer toggles + app shortcuts). Watch for accidental
  triggers on fast rolls (adjacent-key combos like Q+W) and finger-busy chords.
- **Leader sequences** — a large Rectangle/desktop/shortcut tree. Look for
  collisions, unmemorable mnemonics, and gaps.
- **Layer reachability** — every layer should be reachable and escapable without
  contortion; orphan layers are a smell.

## Guardrails

- Confidence-flag every ergonomic claim; much of this is preference, not fact.
- One change at a time when it affects muscle memory; don't bundle a refactor
  with a feature.
- Keep `reference/layout-conventions.md` current: when the user explains a
  preference or rejects an idea and says why, add it there so future proposals
  respect it.
