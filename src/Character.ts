export class Character {
  readonly isAlive: boolean = true;

  private currentHealth: number = 1000;

  get health(): number {
    return this.currentHealth;
  }

  dealDamage(target: Character, damage: number): void {
    target.currentHealth -= damage;
  }
}
