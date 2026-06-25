export interface Target {
  readonly health: number;
  belongsTo(faction: string): boolean;
}
