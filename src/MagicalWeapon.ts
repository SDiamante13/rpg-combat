import { MagicalObject } from './MagicalObject.ts';
import type { Character } from './Character.ts';

export class MagicalWeapon extends MagicalObject {
  constructor(
    maxHealth: number,
    private readonly damage: number,
  ) {
    super(maxHealth);
  }

  override attack(target: Character): void {
    target.takeDamage(this.damage);
    this.takeDamage(1);
  }
}
