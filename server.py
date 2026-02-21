import asyncio
import random
import socketio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
app.mount("/", socketio.ASGIApp(sio, app))

GRID_SIZE = 30
STARTER_ZONE_MIN = 2
STARTER_ZONE_MAX = 8
STARTER_SPAWN = (5, 5)

STARTERS = {
    "bulbasaur": {
        "species": "Bulbasaur",
        "level": 5,
        "moves": ["Tackle", "Growl", "Vine Whip", "Leech Seed"],
    },
    "charmander": {
        "species": "Charmander",
        "level": 5,
        "moves": ["Scratch", "Growl", "Ember", "Smokescreen"],
    },
    "squirtle": {
        "species": "Squirtle",
        "level": 5,
        "moves": ["Tackle", "Tail Whip", "Water Gun", "Withdraw"],
    },
}

grid = []
players = {}


def generate_grid():
    generated = [
        [random.choices(["L", "W"], weights=[0.85, 0.15])[0] for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ]

    for y in range(STARTER_ZONE_MIN, STARTER_ZONE_MAX + 1):
        for x in range(STARTER_ZONE_MIN, STARTER_ZONE_MAX + 1):
            generated[y][x] = "L"

    border_min = STARTER_ZONE_MIN - 1
    border_max = STARTER_ZONE_MAX + 1
    for i in range(border_min, border_max + 1):
        generated[border_min][i] = "T"
        generated[border_max][i] = "T"
        generated[i][border_min] = "T"
        generated[i][border_max] = "T"

    generated[STARTER_SPAWN[1]][STARTER_SPAWN[0]] = "S"
    generated[4][4] = "P"
    generated[4][5] = "P"
    generated[4][6] = "P"

    return generated


# Create global grid on startup
grid = generate_grid()


def random_land_tile():
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if grid[y][x] == "L":
            return x, y


@sio.event
async def connect(sid, environ, auth):
    auth = auth or {}
    name = auth.get("name", "William")
    sprite = auth.get("sprite", "male_1.png")

    progress = auth.get("progress") or {}
    starter_chosen = bool(progress.get("starter_chosen"))

    if starter_chosen:
        x, y = random_land_tile()
    else:
        x, y = STARTER_SPAWN

    player_party = auth.get("party") or []

    players[sid] = {
        "x": x,
        "y": y,
        "name": name,
        "sprite": sprite,
        "progress": {"starter_chosen": starter_chosen},
        "party": player_party,
    }

    await sio.save_session(sid, {
        "name": name,
        "sprite": sprite,
    })

    await sio.emit("state", {
        "grid": grid,
        "player": players[sid],
        "players": players,
        "starter_options": STARTERS,
    }, to=sid)

    if not starter_chosen:
        await sio.emit("starter_selection_required", {
            "options": STARTERS,
            "message": "Choose your first Pokémon before continuing your journey.",
        }, to=sid)

    await sio.emit("players_update", players)


@sio.event
async def choose_starter(sid, data):
    player = players.get(sid)
    if not player:
        return

    if player["progress"].get("starter_chosen"):
        return

    selection = (data or {}).get("starter", "").lower()
    starter = STARTERS.get(selection)
    if not starter:
        await sio.emit("starter_selection_error", {
            "message": "Invalid starter selection.",
        }, to=sid)
        return

    player["party"] = [{"species": starter["species"], "level": starter["level"], "moves": list(starter["moves"])}]
    player["progress"]["starter_chosen"] = True

    await sio.emit("starter_selected", {
        "starter": starter,
        "progress": player["progress"],
        "party": player["party"],
    }, to=sid)
    await sio.emit("players_update", players)


@sio.event
async def move(sid, data):
    direction = data.get("direction")
    pos = players.get(sid)

    if not pos:
        return

    if not pos.get("progress", {}).get("starter_chosen"):
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

    if grid[new_y][new_x] in {"L", "S", "P"}:
        pos["x"], pos["y"] = new_x, new_y
        await sio.emit("players_update", players)


@sio.event
def disconnect(sid):
    print(f"👋 Client disconnected: {sid}")
    players.pop(sid, None)
    asyncio.create_task(sio.emit("players_update", players))


@app.get("/api/player-sprites")
async def get_player_sprites():
    sprite_folder = os.path.join("frontend", "assets", "player")
    sprites = [
        f[:-4] for f in os.listdir(sprite_folder)
        if f.endswith(".png")
    ]
    return JSONResponse(content={"sprites": sprites})
