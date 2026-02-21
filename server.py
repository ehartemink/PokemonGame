import asyncio
import os
import random
import time

import socketio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from persistence import load_or_create_profile, merge_profile_patch, save_profile

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()
app.mount("/", socketio.ASGIApp(sio, app))

GRID_SIZE = 30
AUTOSAVE_SECONDS = 45

grid = []
players = {}
autosave_tasks = {}


def generate_grid():
    return [
        [random.choices(["L", "W"], weights=[0.8, 0.2])[0] for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ]


grid = generate_grid()


def _player_from_profile(profile):
    trainer = profile.get("trainer", {})
    position = trainer.get("position", {})
    return {
        "x": int(position.get("x", 0)),
        "y": int(position.get("y", 0)),
        "name": trainer.get("name", "Trainer"),
        "sprite": trainer.get("sprite", "male_1.png"),
        "trainer_id": trainer.get("id", ""),
        "map_id": trainer.get("map_id", "overworld"),
        "profile": profile,
    }


def _sync_profile_from_player(player):
    trainer = player["profile"].setdefault("trainer", {})
    trainer["id"] = player.get("trainer_id")
    trainer["name"] = player.get("name")
    trainer["sprite"] = player.get("sprite")
    trainer["position"] = {"x": player.get("x", 0), "y": player.get("y", 0)}
    trainer["map_id"] = player.get("map_id", "overworld")


def _save_player_profile(player, reason="manual"):
    _sync_profile_from_player(player)
    now = time.time()
    connected_at = player.get("connected_at", now)
    started_play_time = float(player.get("play_time_at_connect", 0))
    player["profile"]["trainer"]["play_time"] = int(started_play_time + (now - connected_at))
    save_profile(player["profile"])
    print(f"💾 Saved profile for {player.get('name')} ({reason})")


async def _autosave_loop(sid):
    try:
        while True:
            await asyncio.sleep(AUTOSAVE_SECONDS)
            player = players.get(sid)
            if not player:
                return
            _save_player_profile(player, reason="autosave")
    except asyncio.CancelledError:
        return


def _public_players_state():
    return {
        sid: {
            "x": player["x"],
            "y": player["y"],
            "name": player["name"],
            "sprite": player["sprite"],
            "map_id": player.get("map_id", "overworld"),
            "trainer_id": player.get("trainer_id", ""),
        }
        for sid, player in players.items()
    }


@sio.event
async def connect(sid, environ, auth):
    auth = auth or {}
    name = auth.get("name", "William")
    sprite = auth.get("sprite", "male_1.png")

    profile = load_or_create_profile(name=name, sprite=sprite, grid=grid)
    player = _player_from_profile(profile)
    player["connected_at"] = time.time()
    player["play_time_at_connect"] = profile.get("trainer", {}).get("play_time", 0)

    players[sid] = player

    await sio.save_session(sid, {
        "name": player["name"],
        "sprite": player["sprite"],
        "trainer_id": player.get("trainer_id", ""),
    })

    await sio.emit("state", {
        "grid": grid,
        "player": _public_players_state().get(sid),
        "players": _public_players_state(),
        "profile": profile,
    }, to=sid)

    await sio.emit("players_update", _public_players_state())

    autosave_tasks[sid] = asyncio.create_task(_autosave_loop(sid))


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

    if grid[new_y][new_x] == "L":
        moved = pos["x"] != new_x or pos["y"] != new_y
        pos["x"], pos["y"] = new_x, new_y
        if moved:
            await sio.emit("players_update", _public_players_state())


@sio.event
async def map_transition(sid, data):
    player = players.get(sid)
    if not player:
        return
    player["map_id"] = data.get("map_id", player.get("map_id", "overworld"))
    _save_player_profile(player, reason="map_transition")


@sio.event
async def inventory_change(sid, data):
    player = players.get(sid)
    if not player:
        return

    inventory = data.get("inventory")
    if isinstance(inventory, list):
        player["profile"]["inventory"] = inventory
    _save_player_profile(player, reason="inventory_change")


@sio.event
async def battle_end(sid, data):
    player = players.get(sid)
    if not player:
        return

    patch = data.get("profile_patch", {})
    if isinstance(patch, dict):
        merge_profile_patch(player["profile"], patch)

    _save_player_profile(player, reason="battle_end")


@sio.event
def disconnect(sid):
    print(f"👋 Client disconnected: {sid}")

    task = autosave_tasks.pop(sid, None)
    if task:
        task.cancel()

    player = players.pop(sid, None)
    if player:
        _save_player_profile(player, reason="disconnect")

    asyncio.create_task(sio.emit("players_update", _public_players_state()))


@app.get("/api/player-sprites")
async def get_player_sprites():
    sprite_folder = os.path.join("frontend", "assets", "player")
    sprites = [
        f[:-4] for f in os.listdir(sprite_folder)
        if f.endswith(".png")
    ]
    return JSONResponse(content={"sprites": sprites})
