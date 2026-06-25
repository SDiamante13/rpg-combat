import { MagicalObject } from './MagicalObject.ts';
import { HealingObject } from './HealingObject.ts';
import { MagicalWeapon } from './MagicalWeapon.ts';

export function aMagicalObject(maxHealth: number): MagicalObject {
  return new MagicalObject(maxHealth);
}

export function aHealingObject(maxHealth: number): HealingObject {
  return new HealingObject(maxHealth);
}

export function aMagicalWeapon({
  durability,
  damage,
}: {
  durability: number;
  damage: number;
}): MagicalWeapon {
  return new MagicalWeapon(durability, damage);
}
