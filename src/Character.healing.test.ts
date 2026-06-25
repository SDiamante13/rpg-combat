import { describe, expect, it } from 'vitest';

import {
  aCharacter,
  aCharacterAtLevel,
  aCharacterDamagedBy,
  aDeadCharacter,
} from './character-builders.ts';
import { MagicalObject } from './MagicalObject.ts';

describe('Character healing', () => {
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

  it('an ally can heal a damaged ally', () => {
    const healer = aCharacter();
    const ally = aCharacterDamagedBy(100);
    healer.join('The Order');
    ally.join('The Order');

    healer.heal(50, ally);

    expect(ally.health).toBe(950);
  });

  it('rejects healing a dead character', () => {
    const character = aDeadCharacter();

    expect(() => character.heal(50)).toThrow('A dead character cannot heal');
    expect(character.health).toBe(0);
  });

  it('rejects healing a non-ally', () => {
    const healer = aCharacter();
    const stranger = aCharacterDamagedBy(100);

    expect(() => healer.heal(50, stranger)).toThrow('Cannot heal a non-ally');
    expect(stranger.health).toBe(900);
  });

  it('rejects healing a magical object', () => {
    const healer = aCharacter();
    const magicalObject = new MagicalObject(500);

    expect(() => healer.heal(50, magicalObject)).toThrow('Cannot heal a magical object');
    expect(magicalObject.health).toBe(500);
  });

  it("drawing from a healing object heals up to the object's remaining amount", () => {
    const character = aCharacterDamagedBy(600);
    const healingObject = new MagicalObject(500);

    character.drawFrom(healingObject);

    expect(character.health).toBe(900);
  });
});
