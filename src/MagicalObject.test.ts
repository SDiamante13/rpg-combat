import { describe, expect, it } from 'vitest';

import { aMagicalObject } from './magical-object-builders.ts';

describe('MagicalObject', () => {
  it('a magical object starts at its fixed maximum health and no faction', () => {
    const object = aMagicalObject(500);

    expect(object.health).toBe(500);
    expect(object.belongsTo('The Order')).toBe(false);
  });

  it('a magical object is destroyed when its health reaches zero', () => {
    const object = aMagicalObject(100);

    expect(object.isDestroyed).toBe(false);
    object.takeDamage(150);

    expect(object.health).toBe(0);
    expect(object.isDestroyed).toBe(true);
  });
});
