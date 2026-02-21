from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


STAT_ALIASES = {
    "hp": ["hp", "base_hp", "stat_hp"],
    "attack": ["attack", "atk", "base_attack"],
    "defense": ["defense", "def", "base_defense"],
    "special_attack": ["special_attack", "sp_attack", "sp_atk", "special-attack"],
    "special_defense": ["special_defense", "sp_defense", "sp_def", "special-defense"],
    "speed": ["speed", "spd", "base_speed"],
}

NAME_COLUMNS = ["name", "pokemon", "species", "identifier"]
TYPE1_COLUMNS = ["type1", "type_1", "primary_type"]
TYPE2_COLUMNS = ["type2", "type_2", "secondary_type"]
GROWTH_COLUMNS = ["growth_rate", "growth", "exp_curve"]
EXP_YIELD_COLUMNS = ["exp_yield", "base_experience", "base_exp", "experience_yield"]
ID_COLUMNS = ["id", "pokedex", "pokedex_id", "national_id", "number"]


DEFAULT_STATS = {
    "hp": 35,
    "attack": 35,
    "defense": 35,
    "special_attack": 35,
    "special_defense": 35,
    "speed": 35,
}


@dataclass(frozen=True)
class PokemonSpecies:
    id: Optional[int]
    key: str
    name: str
    types: List[str]
    base_stats: Dict[str, int]
    growth_rate: str
    exp_yield: int


class PokemonDataLoader:
    """Load and normalize MVP-ready Pokémon species data from CSV."""

    def __init__(self, csv_path: str = "./data/pokemon.csv") -> None:
        self.csv_path = Path(csv_path)

    def load_species(self) -> Dict[str, PokemonSpecies]:
        if not self.csv_path.exists():
            return {}

        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if not reader.fieldnames:
                return {}

            species_by_key: Dict[str, PokemonSpecies] = {}
            for row in reader:
                species = self._normalize_row(row)
                if species is None:
                    continue
                species_by_key[species.key] = species

            return species_by_key

    def _normalize_row(self, row: Dict[str, str]) -> Optional[PokemonSpecies]:
        name = self._pick(row, NAME_COLUMNS)
        if not name:
            return None

        display_name = self._title_case_name(name)
        key = self.normalize_name_key(name)

        pokemon_id = self._safe_int(self._pick(row, ID_COLUMNS), default=None)
        primary_type = self._normalize_type(self._pick(row, TYPE1_COLUMNS) or "normal")
        secondary_type = self._normalize_type(self._pick(row, TYPE2_COLUMNS))
        types = [t for t in [primary_type, secondary_type] if t]

        base_stats: Dict[str, int] = {}
        for stat_name, aliases in STAT_ALIASES.items():
            raw_value = self._pick(row, aliases)
            base_stats[stat_name] = max(1, self._safe_int(raw_value, DEFAULT_STATS[stat_name]))

        growth_rate = (self._pick(row, GROWTH_COLUMNS) or "medium").strip().lower()
        exp_yield = max(1, self._safe_int(self._pick(row, EXP_YIELD_COLUMNS), 64))

        return PokemonSpecies(
            id=pokemon_id,
            key=key,
            name=display_name,
            types=types,
            base_stats=base_stats,
            growth_rate=growth_rate,
            exp_yield=exp_yield,
        )

    @staticmethod
    def normalize_name_key(name: str) -> str:
        compact = re.sub(r"[^a-z0-9]", "", name.lower())
        return compact or "unknown"

    @staticmethod
    def _normalize_type(type_name: Optional[str]) -> Optional[str]:
        if not type_name:
            return None
        return type_name.strip().lower().replace(" ", "-")

    @staticmethod
    def _pick(row: Dict[str, str], columns: Iterable[str]) -> Optional[str]:
        lowered = {str(k).strip().lower(): v for k, v in row.items()}
        for column in columns:
            value = lowered.get(column)
            if value is not None and str(value).strip() != "":
                return str(value).strip()
        return None

    @staticmethod
    def _safe_int(value: Optional[str], default: Optional[int]) -> Optional[int]:
        if value is None:
            return default
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _title_case_name(name: str) -> str:
        return "-".join(piece.capitalize() for piece in name.strip().split("-"))
