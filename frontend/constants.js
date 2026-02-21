export const MOVEMENT_COMMANDS = Object.freeze({
  UP: "up",
  DOWN: "down",
  LEFT: "left",
  RIGHT: "right"
});

export const TILE_IDS = Object.freeze({
  LAND: "L",
  WATER: "W",
  PATH: "P",
  TALL_GRASS: "G",
  BUILDING: "B"
});

export const ENCOUNTER_RATES = Object.freeze({
  TALL_GRASS: 0.10,
  CAVE: 0.15,
  WATER: 0.08
});

export const EXP_FORMULAS = Object.freeze({
  BASE_EXP_MULTIPLIER: 1.0,
  LEVEL_EXPONENT: 3,
  WIN_BONUS_MULTIPLIER: 1.5
});

export const ITEM_IDS = Object.freeze({
  POKE_BALL: "poke_ball",
  GREAT_BALL: "great_ball",
  POTION: "potion",
  SUPER_POTION: "super_potion",
  ANTIDOTE: "antidote"
});

export const ITEM_STACK_LIMITS = Object.freeze({
  [ITEM_IDS.POKE_BALL]: 99,
  [ITEM_IDS.GREAT_BALL]: 99,
  [ITEM_IDS.POTION]: 99,
  [ITEM_IDS.SUPER_POTION]: 99,
  [ITEM_IDS.ANTIDOTE]: 99
});

export const BATTLE_ACTION_IDS = Object.freeze({
  FIGHT: "fight",
  BAG: "bag",
  POKEMON: "pokemon",
  RUN: "run"
});
