export class MagicalObject {
  constructor(private readonly maxHealth: number) {}

  get health(): number {
    return this.maxHealth;
  }

  belongsTo(_faction: string): boolean {
    return false;
  }
}
