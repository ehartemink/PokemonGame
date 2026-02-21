import json
import random
import re
import time
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

SAVE_DIR = Path("data/saves")

DEFAULT_KEY_BINDINGS = {
    "move_up": ["w", "arrowup"],
    "move_down": ["s", "arrowdown"],
    "move_left": ["a", "arrowleft"],
    "move_right": ["d", "arrowright"],
    "menu": ["escape"],
    "interact": ["space", "enter"],
}

DEFAULT_PROFILE_TEMPLATE: Dict[str, Any] = {
    "trainer": {
        "id": "",
        "name": "",
        "sprite": "male_1.png",
        "position": {"x": 0, "y": 0},
        "map_id": "overworld",
        "money": 3000,
        "play_time": 0,
    },
    "party": [],
    "inventory": [],
    "progress": {
        "starter_chosen": None,
        "badges": [],
        "story_flags": {},
        "seen_pokemon": [],
        "caught_pokemon": [],
    },
    "settings": {
        "volume": {"master": 1.0, "music": 0.8, "sfx": 0.8},
        "key_bindings": DEFAULT_KEY_BINDINGS,
    },
}


def ensure_save_dir() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def _slugify(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip().lower())
    return clean[:32] if clean else "trainer"


def _save_path(trainer_id: str) -> Path:
    return SAVE_DIR / f"{trainer_id}.json"


def _find_profile_by_name(name: str) -> Dict[str, Any] | None:
    target = name.strip().lower()
    if not target:
        return None

    for path in SAVE_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            _quarantine_corrupt_save(path)
            continue

        trainer_name = str(data.get("trainer", {}).get("name", "")).strip().lower()
        if trainer_name == target:
            return data

    return None


def _quarantine_corrupt_save(path: Path) -> None:
    timestamp = int(time.time())
    path.rename(path.with_suffix(path.suffix + f".corrupt.{timestamp}"))


def _spawn_position(grid: List[List[str]]) -> Dict[str, int]:
    if not grid:
        return {"x": 0, "y": 0}

    rows = len(grid)
    cols = len(grid[0])
    for _ in range(500):
        x = random.randint(0, cols - 1)
        y = random.randint(0, rows - 1)
        if grid[y][x] == "L":
            return {"x": x, "y": y}

    return {"x": 0, "y": 0}


def create_default_profile(name: str, sprite: str, grid: List[List[str]]) -> Dict[str, Any]:
    profile = deepcopy(DEFAULT_PROFILE_TEMPLATE)
    trainer_id = f"{_slugify(name)}-{uuid.uuid4().hex[:8]}"
    spawn = _spawn_position(grid)

    profile["trainer"]["id"] = trainer_id
    profile["trainer"]["name"] = name or "Trainer"
    profile["trainer"]["sprite"] = sprite or "male_1.png"
    profile["trainer"]["position"] = spawn

    return profile


def load_or_create_profile(name: str, sprite: str, grid: List[List[str]]) -> Dict[str, Any]:
    ensure_save_dir()

    profile = _find_profile_by_name(name)
    if profile is not None:
        profile.setdefault("trainer", {})["name"] = name or profile["trainer"].get("name", "Trainer")
        if sprite:
            profile["trainer"]["sprite"] = sprite
        return profile

    profile = create_default_profile(name, sprite, grid)
    save_profile(profile)
    return profile


def save_profile(profile: Dict[str, Any]) -> None:
    ensure_save_dir()
    trainer_id = profile.get("trainer", {}).get("id")
    if not trainer_id:
        trainer_id = f"trainer-{uuid.uuid4().hex[:8]}"
        profile.setdefault("trainer", {})["id"] = trainer_id

    path = _save_path(trainer_id)
    payload = json.dumps(profile, indent=2, sort_keys=True)
    path.write_text(payload + "\n")


def merge_profile_patch(profile: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(profile.get(key), dict):
            merge_profile_patch(profile[key], value)
        else:
            profile[key] = value
    return profile
