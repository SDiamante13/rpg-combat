import { describe, expect, it } from 'vitest';

import { aCharacter } from './character-builders.ts';
import { HealingObject } from './HealingObject.ts';

describe('Magical object combat', () => {
  it('a healing object cannot be used to deal damage', () => {
    const character = aCharacter();
    const target = aCharacter();
    const healingObject = new HealingObject(500);

    expect(() => character.attackWith(healingObject, target)).toThrow(
      'This object cannot deal damage',
    );
    expect(target.health).toBe(1000);
  });
});
