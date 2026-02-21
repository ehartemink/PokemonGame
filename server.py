import asyncio
import random
import socketio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

from pokemon_data import PokemonDataLoader
from pokemon_sprites import PokemonSpriteMapper

# Assuming this is already in your file:
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
app.mount("/", socketio.ASGIApp(sio, app))


GRID_SIZE = 30
grid = []
players = {}
pokemon_loader = PokemonDataLoader("./data/pokemon.csv")
pokemon_species = pokemon_loader.load_species()
sprite_mapper = PokemonSpriteMapper("./data/pokemon_graphics_lib")
sprite_mapper.index()


def generate_grid():
    return [
        [random.choices(["L", "W"], weights=[0.8, 0.2])[0] for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ]


# Create global grid on startup
grid = generate_grid()


@sio.event
async def connect(sid, environ, auth):
    name = auth.get("name", "William")
    sprite = auth.get("sprite", "male_1.png")

    # Find land tile
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if grid[y][x] == "L":
            break

    # Store player state
    players[sid] = {
        "x": x,
        "y": y,
        "name": name,
        "sprite": sprite,
        "direction": "down",
    }

    await sio.save_session(sid, {
        "name": name,
        "sprite": sprite
    })

    await sio.emit("state", {
        "grid": grid,
        "player": players[sid],
        "players": players
    }, to=sid)

    await sio.emit("players_update", players)


@sio.event
async def move(sid, data):
    direction = data.get("direction")
    pos = players.get(sid)

    if not pos:
        return

    dx, dy = 0, 0
    if direction == "up":
        dy = -1
    elif direction == "down":
        dy = 1
    elif direction == "left":
        dx = -1
    elif direction == "right":
        dx = 1

    new_x = max(0, min(GRID_SIZE - 1, pos["x"] + dx))
    new_y = max(0, min(GRID_SIZE - 1, pos["y"] + dy))

    pos["direction"] = direction if direction in {"up", "down", "left", "right"} else "down"

    if grid[new_y][new_x] == "L":
        pos["x"], pos["y"] = new_x, new_y

    await sio.emit("players_update", players)


@sio.event
def disconnect(sid):
    print(f"👋 Client disconnected: {sid}")
    players.pop(sid, None)
    asyncio.create_task(sio.emit("players_update", players))


# Menu options are here

@app.get("/api/player-sprites")
async def get_player_sprites():
    sprite_folder = os.path.join("frontend", "assets", "player")
    sprites = [
        f[:-4] for f in os.listdir(sprite_folder)
        if f.endswith(".png")
    ]
    return JSONResponse(content={"sprites": sprites})


@app.get("/api/pokemon-species")
async def get_pokemon_species():
    return JSONResponse(content={
        "species": [
            {
                "id": species.id,
                "key": species.key,
                "name": species.name,
                "types": species.types,
                "base_stats": species.base_stats,
                "growth_rate": species.growth_rate,
                "exp_yield": species.exp_yield,
                "sprite": sprite_mapper.resolve(name=species.name, species_id=species.id),
            }
            for species in pokemon_species.values()
        ]
    })
