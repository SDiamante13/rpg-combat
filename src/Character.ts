import type { MagicalObject } from './MagicalObject.ts';
import type { Target } from './Target.ts';

const BASE_MAX_HEALTH = 1000;
const HIGH_LEVEL_MAX_HEALTH = 1500;
const HIGH_LEVEL = 6;
const LEVEL_GAP_FOR_DAMAGE_MODIFIER = 5;
const REDUCED_DAMAGE_FACTOR = 0.5;
const INCREASED_DAMAGE_FACTOR = 1.5;
const DAMAGE_PER_LEVEL = 1000;
const FACTIONS_FOR_LEVEL = 3;

export class Character implements Target {
  private currentHealth = BASE_MAX_HEALTH;
  private readonly factions = new Set<string>();
  private readonly factionsEverJoined = new Set<string>();
  private currentLevel: number;
  private damageBuffer = 0;

  constructor(startingLevel = 1) {
    this.currentLevel = startingLevel;
  }

  join(faction: string): void {
    this.factions.add(faction);
    this.recordFactionJoined(faction);
  }

  private recordFactionJoined(faction: string): void {
    if (this.factionsEverJoined.has(faction)) return;
    this.factionsEverJoined.add(faction);
    if (this.factionsEverJoined.size % FACTIONS_FOR_LEVEL === 0) this.gainLevel();
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
    return this.currentLevel;
  }

  private gainLevel(): void {
    this.currentLevel += 1;
  }

  private get maxHealth(): number {
    return this.level >= HIGH_LEVEL ? HIGH_LEVEL_MAX_HEALTH : BASE_MAX_HEALTH;
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
    target.takeDamage(applied);
  }

  takeDamage(amount: number): void {
    this.currentHealth = Math.max(0, this.currentHealth - amount);
    if (this.isAlive) this.recordSurvivedDamage(amount);
  }

  private recordSurvivedDamage(amount: number): void {
    this.damageBuffer += amount;
    if (this.damageBuffer < this.level * DAMAGE_PER_LEVEL) return;
    this.damageBuffer = 0;
    this.gainLevel();
  }

  private isAlliedWith(other: Character): boolean {
    return [...this.factions].some((faction) => other.belongsTo(faction));
  }

  private effectiveDamage(target: Character, damage: number): number {
    if (target.level - this.level >= LEVEL_GAP_FOR_DAMAGE_MODIFIER) {
      return damage * REDUCED_DAMAGE_FACTOR;
    }
    if (this.level - target.level >= LEVEL_GAP_FOR_DAMAGE_MODIFIER) {
      return damage * INCREASED_DAMAGE_FACTOR;
    }
    return damage;
  }

  drawFrom(source: MagicalObject): void {
    this.healCharacter(source.drawHealing(), this);
  }

  attackWith(weapon: MagicalObject, target: Character): void {
    weapon.attack(target);
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
