import { Character } from './Character.ts';

export function aCharacter(): Character {
  return new Character();
}

export function aCharacterDamagedBy(amount: number): Character {
  const character = aCharacter();
  aCharacter().dealDamage(character, amount);
  return character;
}

export function aCharacterAtLevel(level: number): Character {
  return new Character(level);
}

export function aDeadCharacter(): Character {
  return aCharacterDamagedBy(1000);
}
