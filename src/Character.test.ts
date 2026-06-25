import { describe, expect, it } from 'vitest';

import { Character } from './Character.ts';

describe('Character', () => {
  it('starts with 1000 health and alive', () => {
    const character = new Character();

    expect(character.health).toBe(1000);
    expect(character.isAlive).toBe(true);
  });

  it('dealDamage subtracts damage from target health', () => {
    const attacker = new Character();
    const target = new Character();

    attacker.dealDamage(target, 100);

    expect(target.health).toBe(900);
  });
});
