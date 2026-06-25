# Backlog

User stories split from [user-stories.md](../../user-stories.md) into independently deliverable slices.

Dependency order:

```
01 Damage and Health
  ├─> 02 Levels
  ├─> 03 Factions
  │      └─> 04 Magical Objects (also needs 01)
  └─> 05 Changing Level (needs 02 + 03)
```

| #   | Story                                        | Slice                                        |
| --- | -------------------------------------------- | -------------------------------------------- |
| 01  | [Damage and Health](01-damage-and-health.md) | Core combat loop                             |
| 02  | [Levels](02-levels.md)                       | Progression mechanics in combat              |
| 03  | [Factions](03-factions.md)                   | Alliances                                    |
| 04  | [Magical Objects](04-magical-objects.md)     | Neutral healing items & weapons (Data split) |
| 05  | [Changing Level](05-changing-level.md)       | Earning levels                               |
