export class Character {
  private currentHealth: number = 1000;

  get health(): number {
    return this.currentHealth;
  }

  get isAlive(): boolean {
    return this.currentHealth > 0;
  }

  dealDamage(target: Character, damage: number): void {
    target.currentHealth = Math.max(0, target.currentHealth - damage);
  }
}
