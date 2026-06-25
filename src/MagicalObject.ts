import type { Target } from './Target.ts';

export class MagicalObject implements Target {
  private currentHealth: number;

  constructor(maxHealth: number) {
    this.currentHealth = maxHealth;
  }

  get health(): number {
    return this.currentHealth;
  }

  get isDestroyed(): boolean {
    return this.currentHealth === 0;
  }

  takeDamage(amount: number): void {
    this.currentHealth = Math.max(0, this.currentHealth - amount);
  }

  belongsTo(_faction: string): boolean {
    return false;
  }

  drawHealing(): number {
    throw new Error('This object cannot heal');
  }
}
