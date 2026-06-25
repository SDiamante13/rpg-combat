export class Character {
  private currentHealth = 1000;
  private readonly factions = new Set<string>();

  constructor(private readonly characterLevel = 1) {}

  belongsTo(faction: string): boolean {
    return this.factions.has(faction);
  }

  get health(): number {
    return this.currentHealth;
  }

  get level(): number {
    return this.characterLevel;
  }

  private get maxHealth(): number {
    return this.level >= 6 ? 1500 : 1000;
  }

  get isAlive(): boolean {
    return this.currentHealth > 0;
  }

  dealDamage(target: Character, damage: number): void {
    if (target === this) {
      throw new Error('A character cannot damage itself');
    }
    const applied = this.effectiveDamage(target, damage);
    target.currentHealth = Math.max(0, target.currentHealth - applied);
  }

  private effectiveDamage(target: Character, damage: number): number {
    if (target.level - this.level >= 5) {
      return damage * 0.5;
    }
    if (this.level - target.level >= 5) {
      return damage * 1.5;
    }
    return damage;
  }

  heal(amount: number): void {
    if (!this.isAlive) {
      throw new Error('A dead character cannot heal');
    }
    this.currentHealth = Math.min(this.maxHealth, this.currentHealth + amount);
  }
}
