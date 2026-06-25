# Story 4: Magical Objects

**Why:** Introduces a new neutral entity — healing items and weapons — that characters interact with. A **Data** split: a distinct object type with its own lifecycle, deliverable independently of character-vs-character combat.

## Acceptance Criteria

- **Given** a Magical Object is created
  **When** inspected
  **Then** it has Health with a fixed maximum and belongs to no Faction.
- **Given** a Magical Object
  **When** its Health reaches 0
  **Then** it is Destroyed.
- **Given** a Character
  **When** it attempts to heal a Magical Object
  **Then** the action is rejected.
- **Given** a Healing Magical Object
  **When** a Character draws from it
  **Then** the Character gains health up to the lesser of the object's remaining amount and the Character's own max.
- **Given** a Healing Magical Object
  **When** it is used to deal damage
  **Then** the action is rejected.
- **Given** a Magical Weapon
  **When** a Character uses it on a target
  **Then** the target takes the weapon's fixed damage and the weapon's Health drops by 1.
- **Given** a Magical Weapon
  **When** it is used to heal
  **Then** the action is rejected.

## Depends on

- Story 1 (Damage and Health)
- Story 3 (Factions) — for ally/non-ally targeting rules
