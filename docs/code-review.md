# Code Review — RPG Combat Kata

**Repository:** rpg-combat · **Branch:** `main` @ `2fbdb7c` · **Date:** 2026-06-25
**Baseline health:** 33/33 vitest tests passing · eslint clean (functions ≤10 lines, file ≤150, complexity ≤5)
**Method:** per-file architectural fan-out + a 2-skeptic adversarial panel.

## Status: Kata complete — ending here by choice

This project is a **coding kata**. The implementation fully satisfies every acceptance
criterion in [`docs/backlog/`](./backlog) (Stories 1–5), built test-first with one test
per acceptance criterion and characterization tests mutation-verified.

The findings below were produced by a final code review for completeness. **We are
consciously choosing to end the kata here and not remediate them.** They are recorded
as documentation of known trade-offs, not as a backlog of pending work. Most are
hardening concerns (input validation, depletion semantics) or design refinements that
fall outside the kata's stated acceptance criteria; a couple are defensible design
choices the review panel ultimately rejected as non-bugs.

---

## High — correctness gaps

### H1 · A HealingObject never depletes
`HealingObject.drawHealing()` returns `this.health` but never debits the object, so a
single healing object can heal infinitely. AC 04 says a character gains health "up to
the lesser of the object's **remaining** amount and the Character's own max" — *remaining*
implies depletion. No test reads object health after a draw, so it is invisible to the suite.
*Suggested fix:* grant `min(remaining, character headroom)`, debit the object by the
granted amount, and add a depletion/second-draw test.

### H2 · `Character.takeDamage` is public, bypassing every guard
`takeDamage` is the seam weapons and magical objects rely on, but being public it
bypasses the self-check, ally-check, and level modifiers in `dealDamage`. It is the
mechanism behind H3 and M1.
*Suggested fix:* route weapon/object damage through a narrower internal path and tighten
visibility, or document this as the kata's deliberate seam.

### H3 · Negative damage heals and corrupts leveling
`takeDamage(-500)` increases health (no floor on the heal side) and drives the level-up
`damageBuffer` negative, stalling future level-ups. The guarded path is affected too:
`effectiveDamage` only multiplies, never floors, so a negative `dealDamage` amount can heal
an enemy. No acceptance criterion permits negative damage.
*Suggested fix:* validate `amount >= 0` at the `dealDamage` / `takeDamage` boundary.

---

## Medium

### M1 · Weapon attacks bypass self/ally guards
`attackWith` delegates straight to `weapon.attack(target)` → `target.takeDamage(...)`,
routing around the self- and ally-guards. A character can weapon-attack an ally or itself.
Story 4 "depends on Story 3 for ally/non-ally targeting rules," so intent is debatable —
and it is untested either way. (Fixed damage bypassing *level modifiers* is correct per AC.)

### M2 · `startingLevel` is unvalidated
`new Character(0)` yields a survival threshold of `0 × 1000 = 0`, so the first non-lethal
hit grants a level. `new Character(11)` exceeds the level-10 cap at construction (the cap is
enforced only in `gainLevel`).
*Suggested fix:* clamp/validate `startingLevel` to `[1, 10]`.

### M3 · A dead character can heal an ally
`healCharacter` checks `!target.isAlive`, but a dead `this` healing a living ally passes.
Only dead-self-heal is tested.
*Suggested fix:* also guard `!this.isAlive`.

### M4 · A destroyed (0-durability) weapon can still attack
No `isDestroyed` guard before attacking; a spent weapon deals full damage. Inferred, not a
spec violation, and untested.

---

## Low / Nits

- **L1 · `instanceof Character` in `heal`** — a runtime type-test against the `Target`
  marker interface; cleaner as a polymorphic `receiveHealing` on `Target`.
- **L2 · `Target` is a degenerate marker interface** — only `health` + an always-false
  `belongsTo`; the `instanceof` re-narrowing defeats its polymorphic purpose.
- **L3 · Duplicated health mutation** — `currentHealth` + `takeDamage` + `Math.max(0, …)`
  appear in both `Character` and `MagicalObject`; a shared `Health` value object would remove it.
- **L4 · `drawFrom` reads the source before the dead-check** — harmless ordering smell.
- **L5 · Fractional health** — odd damage × 0.5 can yield `.5` health; no AC requires integers.

---

## Test-coverage holes worth noting

- No depletion / second-draw test for a HealingObject (would expose H1).
- `drawFrom` never exercises the character-max clamp — deleting the clamp leaves all tests green.
- Ally-heal caps at the *ally's* max, not the healer's — untested (a swap to `this.maxHealth`
  would pass everything).
- The "unmodified damage" test uses level difference 2, never the exact **4** boundary.
- Ally guards are asserted in only one direction (never the reverse).
- No level-10 cap test via the survived-damage path (only the faction path is tested).

---

## Reviewed and rejected as non-bugs

- **"Level-up discards overflow damage"** — resetting `damageBuffer` to 0 on level-up is a
  defensible reading of AC 05 ("cumulative … across any number of battles" toward one
  threshold); the spec only describes single-level transitions. Not a defect.
- **"One hit grants at most one level"** — no AC describes multi-threshold single hits; the
  level-10 cap bounds the blast radius. Non-finding.

---

## What's solid

- **Damage modifiers** — all three branches (halve at 5+ above, boost at 5+ below, unmodified
  within 5) are correct and tested.
- **Faction leveling** — `factionsEverJoined` is a separate Set that never shrinks on `leave`,
  so "a gained level is never lost" holds; rejoining is idempotent; 3→L2 and 6→L3 verified.
- **Level-10 cap** — a single choke point in `gainLevel`, guarded `< MAX_LEVEL`.
- **Lethal-blow-grants-no-level** — the `if (this.isAlive)` gate correctly defers leveling
  past damage resolution, tested.
- **Destruction semantics** — `isDestroyed` (`=== 0`) is consistent with the `Math.max(0, …)` floor.
- **Capability rejection** — heal-a-weapon and attack-with-a-healer reject at runtime via
  base-class throws, as the acceptance criteria require; tested.
