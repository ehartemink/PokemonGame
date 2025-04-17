import asyncio
import random
import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

GRID_SIZE = 30
grid = []
players = {}

def generate_grid():
    return [
        [random.choices(["L", "W"], weights=[0.8, 0.2])[0] for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ]

# Create global grid on startup
grid = generate_grid()

@sio.event
async def connect(sid, environ):
    print(f"✅ Client connected: {sid}")

    # Find a random land tile to spawn player
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if grid[y][x] == "L":
            break

    players[sid] = {"x": x, "y": y}

    # Send initial state only to this client
    await sio.emit("state", {
        "grid": grid,
        "player": players[sid],
        "players": players
    }, to=sid)

    # Notify everyone about the updated players
    await sio.emit("players_update", players)

@sio.event
async def move(sid, data):
    direction = data.get("direction")
    pos = players.get(sid)

    if not pos:
        return

    dx, dy = 0, 0
    if direction == "up": dy = -1
    elif direction == "down": dy = 1
    elif direction == "left": dx = -1
    elif direction == "right": dx = 1

    new_x = max(0, min(GRID_SIZE - 1, pos["x"] + dx))
    new_y = max(0, min(GRID_SIZE - 1, pos["y"] + dy))

    if grid[new_y][new_x] == "L":
        pos["x"], pos["y"] = new_x, new_y
        await sio.emit("players_update", players)

@sio.event
def disconnect(sid):
    print(f"👋 Client disconnected: {sid}")
    players.pop(sid, None)
    asyncio.create_task(sio.emit("players_update", players))
