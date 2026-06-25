import { describe, expect, it } from 'vitest';

import { aCharacter } from './character-builders.ts';
import { aHealingObject, aMagicalWeapon } from './magical-object-builders.ts';

describe('Magical object combat', () => {
  it('a healing object cannot be used to deal damage', () => {
    const character = aCharacter();
    const target = aCharacter();
    const healingObject = aHealingObject(500);

    expect(() => character.attackWith(healingObject, target)).toThrow(
      'This object cannot deal damage',
    );
    expect(target.health).toBe(1000);
  });

  it('a magical weapon cannot be used to heal', () => {
    const character = aCharacter();
    const magicalWeapon = aMagicalWeapon({ durability: 10, damage: 100 });

    expect(() => character.drawFrom(magicalWeapon)).toThrow('This object cannot heal');
  });

  it('a magical weapon deals its fixed damage and loses one health', () => {
    const character = aCharacter();
    const target = aCharacter();
    const weapon = aMagicalWeapon({ durability: 10, damage: 100 });

    character.attackWith(weapon, target);

    expect(target.health).toBe(900);
    expect(weapon.health).toBe(9);
  });
});
