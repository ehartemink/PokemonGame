from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional


class PokemonSpriteMapper:
    """Map Pokémon species names/ids to sprite files with graceful fallback."""

    def __init__(
        self,
        sprites_root: str = "./data/pokemon_graphics_lib",
        placeholder_path: str = "frontend/assets/player/male_1.png",
    ) -> None:
        self.sprites_root = Path(sprites_root)
        self.placeholder_path = Path(placeholder_path)
        self.by_name: Dict[str, str] = {}
        self.by_id: Dict[int, str] = {}
        self._indexed = False

    def index(self) -> None:
        self.by_name.clear()
        self.by_id.clear()

        if not self.sprites_root.exists():
            self._indexed = True
            return

        for file_path in self.sprites_root.rglob("*.png"):
            relative = file_path.as_posix()
            priority = self._sprite_priority(file_path)

            for name_key in self._extract_name_keys(file_path):
                current = self.by_name.get(name_key)
                if current is None or priority < self._sprite_priority(Path(current)):
                    self.by_name[name_key] = relative

            sprite_id = self._extract_id(file_path)
            if sprite_id is not None:
                current = self.by_id.get(sprite_id)
                if current is None or priority < self._sprite_priority(Path(current)):
                    self.by_id[sprite_id] = relative

        self._indexed = True

    def resolve(self, *, name: Optional[str] = None, species_id: Optional[int] = None) -> str:
        if not self._indexed:
            self.index()

        if species_id is not None:
            path = self.by_id.get(species_id)
            if path:
                return path

        if name:
            path = self.by_name.get(self.normalize_name_key(name))
            if path:
                return path

        if self.placeholder_path.exists():
            return self.placeholder_path.as_posix()
        return ""

    @staticmethod
    def normalize_name_key(name: str) -> str:
        return re.sub(r"[^a-z0-9]", "", name.lower())

    @staticmethod
    def _extract_id(path: Path) -> Optional[int]:
        for token in re.findall(r"\d+", path.stem):
            number = int(token)
            if 1 <= number <= 2000:
                return number
        return None

    def _extract_name_keys(self, path: Path) -> set[str]:
        candidates = {path.stem, path.parent.name, f"{path.parent.name}{path.stem}"}
        return {self.normalize_name_key(candidate) for candidate in candidates if candidate}

    @staticmethod
    def _sprite_priority(path: Path) -> int:
        joined = path.as_posix().lower()
        if "front" in joined:
            return 0
        if "normal" in joined:
            return 1
        return 2
