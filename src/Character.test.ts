import { describe, expect, it } from 'vitest';

import { Character } from './Character.ts';

function aCharacter(level = 1): Character {
  return new Character(level);
}

function aCharacterDamagedBy(amount: number): Character {
  const character = aCharacter();
  aCharacter().dealDamage(character, amount);
  return character;
}

function aDeadCharacter(): Character {
  return aCharacterDamagedBy(1000);
}

describe('Character', () => {
  it('starts with 1000 health and alive', () => {
    const character = aCharacter();

    expect(character.health).toBe(1000);
    expect(character.isAlive).toBe(true);
  });

  it('a new character is level 1', () => {
    expect(aCharacter().level).toBe(1);
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

  it('healing an alive character below max increases its health', () => {
    const character = aCharacterDamagedBy(100);

    character.heal(50);

    expect(character.health).toBe(950);
  });

  it('healing cannot raise health above 1000', () => {
    const character = aCharacterDamagedBy(100);

    character.heal(500);

    expect(character.health).toBe(1000);
  });

  it('a level 6+ character can heal up to 1500 health', () => {
    const character = aCharacter(6);

    character.heal(600);

    expect(character.health).toBe(1500);
  });

  it('halves damage when the target is 5+ levels above the attacker', () => {
    const attacker = aCharacter(1);
    const target = aCharacter(6);

    attacker.dealDamage(target, 200);

    expect(target.health).toBe(900);
  });

  it('rejects healing a dead character', () => {
    const character = aDeadCharacter();

    expect(() => character.heal(50)).toThrow('A dead character cannot heal');
    expect(character.health).toBe(0);
  });
});
