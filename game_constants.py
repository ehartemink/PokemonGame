"""Shared game constants for backend systems."""

from types import MappingProxyType

# Movement commands
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
MOVEMENT_COMMANDS = (UP, DOWN, LEFT, RIGHT)

# Tile IDs
LAND = "L"
WATER = "W"
PATH = "P"
TALL_GRASS = "G"
BUILDING = "B"
TILE_IDS = MappingProxyType(
    {
        "LAND": LAND,
        "WATER": WATER,
        "PATH": PATH,
        "TALL_GRASS": TALL_GRASS,
        "BUILDING": BUILDING,
    }
)

# Encounter/balance constants
ENCOUNTER_RATES = MappingProxyType(
    {
        "TALL_GRASS": 0.10,
        "CAVE": 0.15,
        "WATER": 0.08,
    }
)

# EXP formulas and tuning knobs
EXP_FORMULAS = MappingProxyType(
    {
        "BASE_EXP_MULTIPLIER": 1.0,
        "LEVEL_EXPONENT": 3,
        "WIN_BONUS_MULTIPLIER": 1.5,
    }
)

# Inventory IDs and stack limits
ITEM_IDS = MappingProxyType(
    {
        "POKE_BALL": "poke_ball",
        "GREAT_BALL": "great_ball",
        "POTION": "potion",
        "SUPER_POTION": "super_potion",
        "ANTIDOTE": "antidote",
    }
)
ITEM_STACK_LIMITS = MappingProxyType(
    {
        ITEM_IDS["POKE_BALL"]: 99,
        ITEM_IDS["GREAT_BALL"]: 99,
        ITEM_IDS["POTION"]: 99,
        ITEM_IDS["SUPER_POTION"]: 99,
        ITEM_IDS["ANTIDOTE"]: 99,
    }
)

# Battle actions
BATTLE_ACTION_IDS = MappingProxyType(
    {
        "FIGHT": "fight",
        "BAG": "bag",
        "POKEMON": "pokemon",
        "RUN": "run",
    }
)
