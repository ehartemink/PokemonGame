# PokemonGame

A lightweight multiplayer Pokémon-style prototype with:
- a login/character selection screen,
- a tile-based overworld,
- real-time player movement via Socket.IO,
- and basic land/water collision handling.

## Current functionality (baseline)

### 1. Login + character selection
- Players enter a name and choose one of three trainer sprites.
- Selection and name are stored in browser `localStorage`.
- Clicking **Enter World** routes to `world.html`.

### 2. Multiplayer world session
- The client connects to the backend using Socket.IO and sends `name` + `sprite` from `localStorage`.
- Server assigns a random walkable spawn tile.
- Server sends the initial world `state` and broadcasts `players_update` events to all clients.

### 3. Movement + collision
- Keyboard movement supports both WASD and arrow keys.
- Backend validates movement and blocks walking onto water tiles.
- Player labels are drawn under sprites.

### 4. World rendering
- The map is currently generated randomly (land/water) at server startup.
- The client renders solid color tiles (`green` land / `blue` water) and overlays sprites.
- Background music starts after first user input.

## Current project structure

- `server.py`: FastAPI + Socket.IO backend, random map generation, player state, movement checks.
- `frontend/index.html` + `frontend/index.js`: login flow and trainer selection.
- `frontend/world.html` + `frontend/world.js`: map rendering, controls, multiplayer synchronization.
- `frontend/assets/`: player sprites, music, and sound effects.
- `data/pokemon_graphics_lib` (provided): source graphics for future overworld/battle visuals.
- `data/pokemon.csv` (provided): source Pokémon dataset for starter/wild/battle systems.

## Next step
See [`plan.md`](plan.md) for a scoped implementation plan to evolve this prototype into a fuller Pokémon-style game.
