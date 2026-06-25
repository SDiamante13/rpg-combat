# Story 3: Factions

**Why:** Adds alliances, enabling team play — allies can't harm each other and can heal each other. Layers a relationship rule on top of the combat from Stories 1–2.

## Acceptance Criteria

- **Given** a newly created Character
  **When** it is inspected
  **Then** it belongs to no Faction.
- **Given** a Character
  **When** it joins a Faction
  **Then** it is a member.
- **Given** a Character in a Faction
  **When** it leaves the Faction
  **Then** it is no longer a member.
- **Given** a Character
  **When** it joins multiple Factions
  **Then** it belongs to all of them.
- **Given** two Characters sharing a Faction
  **When** one deals damage to the other
  **Then** the action is rejected.
- **Given** two Characters sharing a Faction
  **When** one heals the other
  **Then** the target's Health increases.
- **Given** two Characters sharing no Faction
  **When** one attempts to heal the other
  **Then** the action is rejected.

## Depends on

- Story 1 (Damage and Health)
