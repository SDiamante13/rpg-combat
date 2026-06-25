import { describe, expect, it } from 'vitest';

import { aCharacter } from './character-builders.ts';

describe('Character combat', () => {
  it('starts with 1000 health and alive', () => {
    const character = aCharacter();

    expect(character.health).toBe(1000);
    expect(character.isAlive).toBe(true);
  });

  it('dealDamage subtracts damage from target health', () => {
    const target = aCharacter();

    aCharacter().dealDamage(target, 100);

    expect(target.health).toBe(900);
  });

  it('lethal damage floors health at zero and kills the target', () => {
    const target = aCharacter();

    aCharacter().dealDamage(target, 1200);

    expect(target.health).toBe(0);
    expect(target.isAlive).toBe(false);
  });

  it('rejects dealing damage to itself', () => {
    const character = aCharacter();

    expect(() => character.dealDamage(character, 100)).toThrow('A character cannot damage itself');
    expect(character.health).toBe(1000);
  });

  it('allies sharing a faction cannot damage each other', () => {
    const attacker = aCharacter();
    const target = aCharacter();
    attacker.join('The Order');
    target.join('The Order');

    expect(() => attacker.dealDamage(target, 200)).toThrow('Allies cannot damage each other');
    expect(target.health).toBe(1000);
  });
});
