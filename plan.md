# Pokémon Game Augmentation Plan

This plan turns the current multiplayer movement prototype into a structured Pokémon-style game with persistence, progression, encounters, and battles.

---

## 0) Product goals

Deliver an MVP that supports:
1. Persistent trainer profile across runs.
2. Starter Pokémon selection and party ownership.
3. Inventory (view + update + save).
4. Centralized command/constants definitions.
5. Image-based overworld (grass/water tiles).
6. Authored, plausible map (town/routes/paths/water/grass patches).
7. Camera panning as player approaches boundaries.
8. Tall-grass encounters with wild Pokémon.
9. Turn-based wild battle system with EXP gain.
10. Core Pokémon loop glue (healing, save/load, basic progression).

---

## 1) Architecture and data model foundation

### 1.1 Create shared game constants
- Add a dedicated module (e.g., `game_constants.py` + `frontend/constants.js` or a generated JSON) for:
  - movement commands (`UP`, `DOWN`, `LEFT`, `RIGHT`),
  - tile IDs (`LAND`, `WATER`, `PATH`, `TALL_GRASS`, `BUILDING`, etc.),
  - encounter rates,
  - EXP formulas,
  - inventory item IDs and stack limits,
  - battle action IDs.
- Replace hard-coded movement strings and tile literals with centralized constants.

### 1.2 Define persistent player profile schema
Create a canonical profile object (JSON-serializable):
- `trainer`: id/name/sprite/position/map_id/money/play_time.
- `party`: list of owned Pokémon with level, exp, hp/stats, moves.
- `inventory`: item stacks.
- `progress`: starter chosen, badges, story flags, seen/caught Pokémon.
- `settings`: volume, key bindings (future-proofing).

### 1.3 Persistence engine
- Add persistence layer on backend (start with local JSON files under `data/saves/` keyed by trainer name or generated ID).
- Implement:
  - load-on-login,
  - save on key state transitions (battle end, inventory change, map transition),
  - periodic autosave (e.g., every 30–60s),
  - graceful fallback for missing/corrupt saves.

---

## 2) Starter Pokémon and Pokédex data integration

### 2.1 Parse Pokémon data source
- Build a loader for `./data/pokemon.csv` with fields required for MVP battles:
  - name, types, base stats, growth rate/exp yield (or approximated values).
- Add validation and normalization pass (e.g., lowercase keys, stat defaults).

### 2.2 Starter selection flow
- After login (or first load), if no starter exists:
  - route player to starter selection UI,
  - offer 3 curated starter choices,
  - initialize chosen Pokémon at level 5 with sensible starter moves,
  - set `progress.starter_chosen = true` and save.

### 2.3 Sprite/data assets mapping
- Build mapping layer from Pokémon species name/id to files in `./data/pokemon_graphics_lib`.
- Add fallback placeholder if a sprite file is missing.

---

## 3) Inventory system

### 3.1 Inventory domain model
- Implement stack-based inventory object:
  - item id, display name, quantity, max stack, category.
- Seed starter inventory (e.g., Poké Balls, Potion).

### 3.2 Inventory UI
- Add inventory screen/modal with:
  - list of items,
  - counts,
  - basic usage actions (Potion in battle/overworld if desired for MVP).
- Bind open/close to a centralized command constant.

### 3.3 Inventory mutation APIs
- Backend functions for `add_item`, `remove_item`, `has_item`.
- Save inventory after mutation.

---

## 4) Overworld map and rendering improvements

### 4.1 Replace random map with authored map
- Create static map file (JSON/CSV/tilemap-like) including:
  - town spawn area,
  - route paths,
  - water bodies,
  - blocked terrain,
  - tall-grass encounter zones.
- Optionally split into chunks/maps for future scaling.

### 4.2 Use tile images (grass/water)
- Replace color fills with image-based tiles.
- Load grass/water textures from `./data/pokemon_graphics_lib` (or copied frontend assets).
- Add image preloading and fallback color fill if asset load fails.

### 4.3 Camera/panning system
- Keep player near screen center while moving.
- Implement camera offset clamped to map edges for natural boundary behavior.
- Render only visible tile window for performance.

### 4.4 Collision + zone metadata
- Differentiate tile flags:
  - walkable,
  - surf-only,
  - encounter-enabled,
  - blocked.
- Movement logic reads tile metadata rather than literal tile chars.

---

## 5) Encounter system (tall grass)

### 5.1 Trigger model
- On step into tall grass, roll random encounter chance based on constants.
- Add anti-spam logic (step cooldown / grace steps after battle).

### 5.2 Wild Pokémon generation
- Per-zone encounter table:
  - species list,
  - level range,
  - encounter weights.
- Instantiate wild Pokémon from species data + generated level/stats.

### 5.3 Battle transition
- Freeze overworld movement during battle.
- Enter battle scene/state machine and restore overworld on battle end.

---

## 6) Wild battle MVP

### 6.1 Battle state machine
Implement states like:
- `BATTLE_START`
- `PLAYER_CHOOSE_ACTION`
- `PLAYER_MOVE`
- `WILD_MOVE`
- `RESOLVE_TURN`
- `BATTLE_END`

### 6.2 Core combat rules
- Turn order by speed (or simple player-first for MVP).
- Move damage using simple Pokémon-like formula.
- HP/faint handling.
- Run action for escape chance.

### 6.3 Rewards and persistence
- On wild faint:
  - grant EXP to active party Pokémon,
  - level-up if threshold crossed,
  - persist updated party.
- Optional MVP extension: catch mechanics with Poké Balls.

### 6.4 Battle UI
- Show player Pokémon + wild Pokémon sprites, HP bars, level labels, move menu, and battle log text.

---

## 7) Additional “Pokémon feel” features (recommended)

1. **Pokémon Center / healing tile**: restore party HP and save.
2. **Simple NPC interactions**: dialogue boxes and tutorial hints.
3. **Pause/menu hub**: party, inventory, save, settings.
4. **Audio transitions**: route music vs battle music with fade.
5. **Basic quest flags**: first grass battle, first heal, etc.

---

## 8) Delivery phases (incremental roadmap)

### Phase 1: Core foundations
- Constants module, save/load system, schema versioning.
- Static map loading and tile metadata.

### Phase 2: Starter + inventory
- Starter selection flow.
- Inventory data model + UI + persistence.

### Phase 3: Visual world upgrade
- Image-based grass/water tiles.
- Camera panning and edge clamping.

### Phase 4: Encounters + battle MVP
- Tall grass encounter rolls.
- Wild battle loop and EXP rewards.

### Phase 5: Polish
- Healing area, menu UX, audio polish, balancing, bug fixes.

---

## 9) Technical guardrails

- Keep all command strings and tile keys in constants.
- Use deterministic IDs in persisted data (avoid display-name keys).
- Add save schema version field for migration safety.
- Keep battle and overworld logic in separate modules.
- Add lightweight tests for:
  - save/load integrity,
  - encounter RNG boundaries,
  - EXP and level-up math,
  - movement collision correctness.

---

## 10) Definition of done for requested scope

The scope is complete when a player can:
1. Log in, keep their profile across app restarts.
2. Select a starter once, see it in their party.
3. Open and view inventory with persistent item counts.
4. Move in a believable map with image tiles and smooth camera panning.
5. Enter tall grass, trigger wild encounter, complete battle, and gain EXP.
6. Continue progression after reload with data intact.
