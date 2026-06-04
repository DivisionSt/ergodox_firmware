---
name: updating-kle
description: Proposes targeted, human-reviewed edits to the hand-curated KLE file (kle/divisionst_ergodox.json) when firmware keycodes change. Use when a layout change should be reflected in the keyboard-layout-editor file, or when the user asks to update the KLE / layout image. Never regenerates or overwrites the file.
---

# Updating the KLE

`kle/divisionst_ergodox.json` is **hand-curated** by the user. Each physical key
packs several firmware layers into KLE's 12 legend slots, color-coded by layer.
This file is precious craft — the job here is to propose **surgical, single-legend
edits** that keep it current with the firmware, never to regenerate it.

**Hard rules:**
- Never re-serialize the JSON (that reflows the hand formatting). Make changes as
  targeted text replacements with the Edit tool, on one legend string at a time.
- Never edit without showing the user the before/after and getting agreement.
- Icon legends (`<i class='fa…'>`, `<i class='mss…'>`) cannot be derived from a
  keycode — flag them for the user to set visually; do not guess.

## The slot/color convention

Legends are `\n`-joined into 12 slots; colors live in the key's `t` property in
the same slot order. The layer each slot+color encodes is in
`tools/keymap/maps/kle_encoding.tsv`:

| slot | color | layer |
|------|-------|-------|
| 0 | black `#000000` | base |
| 3 | magenta `#a416a9` | shifted/alt symbol |
| 4 | red `#ab0000` | device / Bluetooth / reset |
| 4 | green `#348f03` | function keys |
| 9 / 11 | blue `#1f19fa` | nav / media |

## Workflow

```
- [ ] 1. Identify what changed (keycode + which firmware layer)
- [ ] 2. Decode the affected KLE key
- [ ] 3. Propose the single-slot legend edit
- [ ] 4. Apply via Edit (surgical text replace), then lint
- [ ] 5. Show the user; they confirm or adjust
```

**1. Identify the change.** Usually from a parity run or a firmware diff: e.g.
"base-mac key `6` became `7`" or "ext-func gained `F12` on the `Y` key."

**2. Decode the key.** Find it by its base legend:

```bash
python3 tools/keymap/kle.py --show Y
```

This prints each populated slot with its slot index, color, decoded layer, and
current legend. Use it to locate the exact slot that needs to change for the
layer that changed.

**3. Propose the edit.** Map the new keycode to its human legend (e.g. `KC_F12`
→ `F12`, `KC_SLASH` → `/`). Identify the target slot from step 2. Show the user
the current vs. proposed legend string.

**4. Apply surgically.** Read the relevant lines of `kle/divisionst_ergodox.json`
and use Edit to replace just that legend string. Keep the slot count (number of
`\n`) and the matching `t` color string intact. Then lint:

```bash
python3 tools/keymap/kle.py --lint    # confirms all keys still within 12 slots
```

**5. Review.** Summarize what changed and confirm with the user. The PNG
(`kle/divisionst_ergodox.png`) is exported from KLE by the user, not generated
here — remind them to re-export if they want the image refreshed.

## Linking firmware positions to KLE keys

The KLE has its own geometry and is keyed by human legends, not firmware matrix
positions, so the link is by legend/meaning and needs judgment. When a base
legend is ambiguous (repeated, or an icon), surface the candidates from
`kle.py --show` and ask the user which physical key they mean.
