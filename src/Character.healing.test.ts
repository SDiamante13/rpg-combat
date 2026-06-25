import { describe, expect, it } from 'vitest';

import { aCharacterAtLevel, aCharacterDamagedBy, aDeadCharacter } from './character-builders.ts';

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

  it('rejects healing a dead character', () => {
    const character = aDeadCharacter();

    expect(() => character.heal(50)).toThrow('A dead character cannot heal');
    expect(character.health).toBe(0);
  });
});
