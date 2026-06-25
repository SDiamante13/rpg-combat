# Story 1: Damage and Health

**Why:** Establishes the core combat loop — characters can hurt, kill, and heal. Nothing else in the engine works without this foundation, and on its own it already supports a playable fight.

## Acceptance Criteria

- **Given** a newly created Character
  **When** it is inspected
  **Then** its Health is 1000 and it is Alive.
- **Given** two Characters
  **When** one deals damage to the other
  **Then** the damage is subtracted from the target's Health.
- **Given** a Character receives damage exceeding its current Health
  **When** the hit resolves
  **Then** its Health becomes 0 and it is Dead.
- **Given** a Character
  **When** it attempts to deal damage to itself
  **Then** the action is rejected.
- **Given** an Alive Character below max Health
  **When** it heals itself
  **Then** its Health increases.
- **Given** a Dead Character
  **When** it attempts to heal
  **Then** the action is rejected.
