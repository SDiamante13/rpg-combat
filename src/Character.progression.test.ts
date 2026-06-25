import { describe, expect, it } from 'vitest';

import { aCharacter, aCharacterAtLevel } from './character-builders.ts';

describe('Character progression', () => {
  it('a character that survives 1000 cumulative damage gains a level', () => {
    const character = aCharacter();
    const attacker = aCharacter();

    attacker.dealDamage(character, 500);
    character.heal(500);
    attacker.dealDamage(character, 500);
    character.heal(500);

    expect(character.isAlive).toBe(true);
    expect(character.level).toBe(2);
  });

  it('a level 2 character needs more than 1000 survived damage to gain a level', () => {
    const character = aCharacterAtLevel(2);
    const attacker = aCharacter();

    attacker.dealDamage(character, 500);
    character.heal(500);
    attacker.dealDamage(character, 500);
    character.heal(500);

    expect(character.isAlive).toBe(true);
    expect(character.level).toBe(2);
  });

  it('a lethal blow that crosses the level-up threshold grants no level', () => {
    const character = aCharacter();
    const attacker = aCharacter();

    attacker.dealDamage(character, 500);
    attacker.dealDamage(character, 500);

    expect(character.isAlive).toBe(false);
    expect(character.level).toBe(1);
  });
});
