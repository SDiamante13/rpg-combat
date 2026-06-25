import type { Target } from './Target.ts';

export class Character implements Target {
  private currentHealth = 1000;
  private readonly factions = new Set<string>();

  constructor(private readonly characterLevel = 1) {}

  join(faction: string): void {
    this.factions.add(faction);
  }

  leave(faction: string): void {
    this.factions.delete(faction);
  }

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
    if (this.isAlliedWith(target)) {
      throw new Error('Allies cannot damage each other');
    }
    const applied = this.effectiveDamage(target, damage);
    target.currentHealth = Math.max(0, target.currentHealth - applied);
  }

  private isAlliedWith(other: Character): boolean {
    return [...this.factions].some((faction) => other.belongsTo(faction));
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

  heal(amount: number, target: Target = this): void {
    if (!(target instanceof Character)) throw new Error('Cannot heal a magical object');
    this.healCharacter(amount, target);
  }

  private healCharacter(amount: number, target: Character): void {
    if (!target.isAlive) throw new Error('A dead character cannot heal');
    if (target !== this && !this.isAlliedWith(target)) throw new Error('Cannot heal a non-ally');
    target.currentHealth = Math.min(target.maxHealth, target.currentHealth + amount);
  }
}
