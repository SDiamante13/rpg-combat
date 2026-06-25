export class Character {
  private static readonly maxHealth = 1000;

  private currentHealth: number = Character.maxHealth;

  get health(): number {
    return this.currentHealth;
  }

  get level(): number {
    return 1;
  }

  get isAlive(): boolean {
    return this.currentHealth > 0;
  }

  dealDamage(target: Character, damage: number): void {
    if (target === this) {
      throw new Error('A character cannot damage itself');
    }
    target.currentHealth = Math.max(0, target.currentHealth - damage);
  }

  heal(amount: number): void {
    if (!this.isAlive) {
      throw new Error('A dead character cannot heal');
    }
    this.currentHealth = Math.min(Character.maxHealth, this.currentHealth + amount);
  }
}
