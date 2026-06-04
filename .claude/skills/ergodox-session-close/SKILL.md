---
name: ergodox-session-close
description: Repo-specific session-close for the ergodox_firmware repo. Runs the QMK/ZMK parity and invariant guard, refreshes the generated LAYERS.md, flags KLE and hardware-build follow-ups, then does the git commit-push-PR close following this repo's conventions. Invoked by the global session-close skill, which owns memory and notes and delegates this repo's verification and git close here.
---

# ergodox_firmware session close

This skill owns the **verification + git close** for this repo. It is normally
reached by delegation from the global `session-close` skill, which has already
handled memory (Step 1) and durable notes (Step 2). **Do not redo memory or
general notes here.**

> If you reached this skill directly (not via the global `session-close`), do
> the global skill's memory and notes steps first, then continue here.

Why this exists: the signature risk in this repo is editing one firmware and
silently drifting from the other. A generic commit-and-push would miss it. This
close gates on parity instead.

## Workflow

Copy this checklist and check off as you go:

```
- [ ] 1. Assess what changed
- [ ] 2. Invariant + parity guard (if a keymap or maps changed)
- [ ] 3. Refresh generated artifacts (LAYERS.md)
- [ ] 4. Flag follow-ups (KLE staleness, layout decisions)
- [ ] 5. Hardware-honesty reminder (if firmware changed)
- [ ] 6. Git close (repo conventions)
- [ ] 7. Summary
```

### 1. Assess what changed

```bash
git status --short
git diff --stat $(git merge-base HEAD origin/main)..HEAD
```

Note whether these changed: `DYrAK/keymap.c` (QMK), `config/*.keymap` /
`config/*.dtsi` (ZMK), or `tools/keymap/maps/*`.

### 2. Invariant + parity guard

Run only if a keymap or a `tools/keymap/maps/` file changed.

```bash
python3 tools/keymap/selfcheck.py        # MUST pass
python3 tools/keymap/parity.py --summary
```

- **`selfcheck.py` failing is a HARD STOP.** A broken invariant (key count off,
  position map not a permutation, base-mac anchor moved) means the parsers/maps
  no longer match the firmware. Surface it and resolve before committing firmware
  changes on top of it. Do not close dirty.
- Report the parity drift and unmapped totals. If **unmapped rose**, a keycode
  is missing from `tools/keymap/maps/keycode_map.tsv` — add a row, or confirm
  it's a real divergence and say so. **Never auto-resolve drift**; surface it and
  let the user decide which firmware is canonical.

### 3. Refresh generated artifacts

If `config/slicemk_ergodox.keymap` changed:

```bash
python3 tools/keymap/layers.py --write
git diff --stat LAYERS.md
```

If `LAYERS.md` changed, it is part of this session's work — stage it. `LAYERS.md`
is generated; never hand-edit it.

### 4. Flag follow-ups (do not auto-fix)

- **KLE.** If a base-layer keycode changed, the hand-curated
  `kle/divisionst_ergodox.json` may be stale. Recommend the `updating-kle` skill.
  **Never edit the KLE here**, and never regenerate it.
- **Layout decisions.** Confirm any layout decision or stated preference from
  this session is recorded in
  `.claude/skills/optimizing-layout/reference/layout-conventions.md` (the
  `optimizing-layout` skill's durable design memory). If the global notes step
  missed one, add it now. This is a repo-specific backstop, not a redo of the
  generic notes step.

### 5. Hardware-honesty reminder

If firmware changed, state in the summary — plainly — that the change is **not
verified until a CI build and a flash**:

- QMK (`DYrAK/` changed) → run the `fetch-and-build-layout` Action.
- ZMK (`config/` changed) → run the `build-zmk-layout` Action.

Never describe a firmware change as working or verified. Builds are CI-only;
this tooling is static analysis.

### 6. Git close (repo conventions)

- **Never commit to `main`.** If on `main` with changes, branch first
  (`feat/…` or `chore/…`).
- Atomic commit: present-tense imperative subject, why-focused body, ending with
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- Push the branch and open a PR against `main` (unless the user said hold). End
  the PR body with the Claude Code footer.
- Verify the push landed: `git log origin/<branch>..HEAD` should be empty.

### 7. Summary

Report: selfcheck result; parity totals and whether drift/unmapped changed;
whether `LAYERS.md` was regenerated; any KLE or layout-decision follow-ups
flagged; the hardware reminder if firmware changed; and what was committed,
pushed, and PR'd.

## Guardrails

- `selfcheck.py` failure is a hard stop.
- Never regenerate or overwrite the KLE.
- Never claim hardware verification.
- Never auto-resolve parity drift — surface it; the user decides.
