import { describe, expect, it } from 'vitest';

import { MagicalObject } from './MagicalObject.ts';

describe('MagicalObject', () => {
  it('a magical object starts at its fixed maximum health and no faction', () => {
    const object = new MagicalObject(500);

    expect(object.health).toBe(500);
    expect(object.belongsTo('The Order')).toBe(false);
  });
});
