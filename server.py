import asyncio
import random
import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

GRID_SIZE = 30
PLAYER_START = {"x": 0, "y": 0}
players = {}

def generate_grid():
    return [
        [random.choices(["L", "W"], weights=[0.8, 0.2])[0] for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ]

@sio.event
async def connect(sid, environ):
    print(f"✅ Client connected: {sid}")
    grid = generate_grid()
    players[sid] = PLAYER_START.copy()
    await sio.save_session(sid, {"grid": grid})  # MUST await this
    await sio.emit("state", {"grid": grid, "player": players[sid]}, to=sid)

@sio.event
async def move(sid, data):
    print(f"➡️ Move from {sid}: {data}")
    session = await sio.get_session(sid)
    if not session or "grid" not in session:
        print(f"⚠️ No grid in session for sid {sid}")
        return

    grid = session["grid"]
    pos = players.get(sid)
    if not pos:
        print(f"⚠️ No player position for sid {sid}")
        return

    dx, dy = 0, 0
    direction = data.get("direction")

    if direction == "up": dy = -1
    elif direction == "down": dy = 1
    elif direction == "left": dx = -1
    elif direction == "right": dx = 1

    new_x = max(0, min(GRID_SIZE - 1, pos["x"] + dx))
    new_y = max(0, min(GRID_SIZE - 1, pos["y"] + dy))

    if grid[new_y][new_x] == "L":
        pos["x"], pos["y"] = new_x, new_y
        await sio.emit("player_update", {"player": pos}, to=sid)

@sio.event
def disconnect(sid):
    print(f"👋 Client disconnected: {sid}")
    players.pop(sid, None)
