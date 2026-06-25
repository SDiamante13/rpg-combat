import { describe, expect, it } from 'vitest';

import { Character } from './Character.ts';

describe('Character', () => {
  it('starts with 1000 health and alive', () => {
    const character = new Character();

    expect(character.health).toBe(1000);
    expect(character.isAlive).toBe(true);
  });

  it('a new character is level 1', () => {
    const character = new Character();

    expect(character.level).toBe(1);
  });

  it('dealDamage subtracts damage from target health', () => {
    const attacker = new Character();
    const target = new Character();

    attacker.dealDamage(target, 100);

    expect(target.health).toBe(900);
  });

  it('lethal damage floors health at zero and kills the target', () => {
    const attacker = new Character();
    const target = new Character();

    attacker.dealDamage(target, 1200);

    expect(target.health).toBe(0);
    expect(target.isAlive).toBe(false);
  });

  it('rejects dealing damage to itself', () => {
    const character = new Character();

    expect(() => character.dealDamage(character, 100)).toThrow('A character cannot damage itself');
    expect(character.health).toBe(1000);
  });

  it('healing an alive character below max increases its health', () => {
    const attacker = new Character();
    const character = new Character();
    attacker.dealDamage(character, 100);

    character.heal(50);

    expect(character.health).toBe(950);
  });

  it('healing cannot raise health above 1000', () => {
    const attacker = new Character();
    const character = new Character();
    attacker.dealDamage(character, 100);

    character.heal(500);

    expect(character.health).toBe(1000);
  });

  it('rejects healing a dead character', () => {
    const attacker = new Character();
    const character = new Character();
    attacker.dealDamage(character, 1000);

    expect(() => character.heal(50)).toThrow('A dead character cannot heal');
    expect(character.health).toBe(0);
  });
});
