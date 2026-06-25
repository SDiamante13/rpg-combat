import { describe, expect, it } from 'vitest';

import { Character } from './Character.ts';

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
    const character = aCharacterAtLevel(6);

    character.heal(600);

    expect(character.health).toBe(1500);
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

  it('a new character belongs to no faction', () => {
    expect(aCharacter().belongsTo('The Order')).toBe(false);
  });

  it('joining a faction makes the character a member', () => {
    const character = aCharacter();

    character.join('The Order');

    expect(character.belongsTo('The Order')).toBe(true);
  });

  it('joining multiple factions makes the character a member of all of them', () => {
    const character = aCharacter();

    character.join('The Order');
    character.join('The Shadows');

    expect(character.belongsTo('The Order')).toBe(true);
    expect(character.belongsTo('The Shadows')).toBe(true);
  });

  it('leaving a faction removes membership', () => {
    const character = aCharacter();
    character.join('The Order');

    character.leave('The Order');

    expect(character.belongsTo('The Order')).toBe(false);
  });

  it('rejects healing a dead character', () => {
    const character = aDeadCharacter();

    expect(() => character.heal(50)).toThrow('A dead character cannot heal');
    expect(character.health).toBe(0);
  });
});

function aCharacter(): Character {
  return new Character();
}

function aCharacterDamagedBy(amount: number): Character {
  const character = aCharacter();
  aCharacter().dealDamage(character, amount);
  return character;
}

function aCharacterAtLevel(level: number): Character {
  return new Character(level);
}

function aDeadCharacter(): Character {
  return aCharacterDamagedBy(1000);
}
