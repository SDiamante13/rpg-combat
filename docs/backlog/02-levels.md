# Story 2: Levels

**Why:** Introduces character progression and makes combat tactical — level gaps change how much damage lands and how much health a character can hold. Builds on Story 1.

## Acceptance Criteria

- **Given** a newly created Character
  **When** it is inspected
  **Then** its Level is 1.
- **Given** a Character below level 6
  **When** it heals
  **Then** its Health cannot exceed 1000.
- **Given** a Character at level 6 or above
  **When** it heals
  **Then** its Health may rise up to 1500.
- **Given** an attacker and a target 5+ levels above the attacker
  **When** damage is dealt
  **Then** the damage is reduced by 50%.
- **Given** an attacker and a target 5+ levels below the attacker
  **When** damage is dealt
  **Then** the damage is increased by 50%.
- **Given** a level difference of fewer than 5 either way
  **When** damage is dealt
  **Then** damage is unmodified.

## Depends on

- Story 1 (Damage and Health)
