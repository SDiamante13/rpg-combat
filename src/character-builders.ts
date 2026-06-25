import { Character } from './Character.ts';

export function aCharacter(): Character {
  return new Character();
}

export function aCharacterDamagedBy(amount: number): Character {
  const character = aCharacter();
  const damager = aCharacter();
  damager.dealDamage(character, amount);
  return character;
}

export function aCharacterAtLevel(level: number): Character {
  return new Character(level);
}

export function makeAllies(first: Character, second: Character, faction = 'The Order'): void {
  first.join(faction);
  second.join(faction);
}

export function aDeadCharacter(): Character {
  return aCharacterDamagedBy(1000);
}
