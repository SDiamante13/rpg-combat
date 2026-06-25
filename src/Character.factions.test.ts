import { describe, expect, it } from 'vitest';

import { aCharacter } from './character-builders.ts';

describe('Character factions', () => {
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
});
