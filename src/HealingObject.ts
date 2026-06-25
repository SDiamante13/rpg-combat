import { MagicalObject } from './MagicalObject.ts';

export class HealingObject extends MagicalObject {
  override drawHealing(): number {
    return this.health;
  }
}
