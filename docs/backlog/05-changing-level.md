# Story 5: Changing Level

**Why:** Closes the progression loop — characters earn the levels that Story 2 made meaningful, through surviving damage or joining factions. Capstone that ties combat, factions, and levels together.

## Acceptance Criteria

- **Given** a level 1 Character
  **When** it survives a cumulative 1000 damage points across any number of battles
  **Then** it gains a level afterwards (only if still alive).
- **Given** a Character receiving damage that would trigger a level-up
  **When** the hit lands
  **Then** the level is granted directly after the damage resolves, not during.
- **Given** a level N Character
  **When** computing its next threshold
  **Then** it must survive an additional N×1000 damage points to gain the next level.
- **Given** a level 1 Character
  **When** it has ever been part of 3 distinct Factions
  **Then** it gains a level.
- **Given** a level N Character
  **When** it joins 3 more distinct Factions
  **Then** it gains a level.
- **Given** a Character at level 10
  **When** further level-up conditions are met
  **Then** it does not exceed level 10.
- **Given** a Character that has gained a level
  **When** any event occurs
  **Then** it never loses that level.

## Depends on

- Story 1 (Damage and Health)
- Story 2 (Levels)
- Story 3 (Factions)
