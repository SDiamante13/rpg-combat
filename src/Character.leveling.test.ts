import { describe, expect, it } from 'vitest';

import { aCharacter, aCharacterAtLevel } from './character-builders.ts';

describe('Character leveling', () => {
  it('a new character is level 1', () => {
    expect(aCharacter().level).toBe(1);
  });

  it('halves damage when the target is 5+ levels above the attacker', () => {
    const attacker = aCharacterAtLevel(1);
    const target = aCharacterAtLevel(6);

    attacker.dealDamage(target, 200);

    expect(target.health).toBe(900);
  });

  it('boosts damage by 50% when the target is 5+ levels below the attacker', () => {
    const attacker = aCharacterAtLevel(6);
    const target = aCharacterAtLevel(1);

    attacker.dealDamage(target, 200);

    expect(target.health).toBe(700);
  });

  it('leaves damage unmodified when levels differ by fewer than 5', () => {
    const attacker = aCharacterAtLevel(3);
    const target = aCharacterAtLevel(5);

    attacker.dealDamage(target, 200);

    expect(target.health).toBe(800);
  });
});
