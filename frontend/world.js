import { MOVEMENT_COMMANDS, TILE_IDS } from "./constants.js";

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const TILE_SIZE = 25;
let grid = null;
let player = { x: 0, y: 0 };
let players = {};

const socket = io("http://localhost:8000", {
  auth: {
    name: localStorage.getItem("playerName"),
    sprite: localStorage.getItem("playerSprite")
  }
});

socket.on("state", (data) => {
  grid = data.grid;
  player = data.player;
  players = data.players;

  const rows = grid.length;
  const cols = grid[0].length;

  canvas.width = cols * TILE_SIZE;
  canvas.height = rows * TILE_SIZE;

  draw();
});

socket.on("players_update", (data) => {
  players = data;
  draw();
});

const spriteCache = {};
const KEY_TO_DIRECTION = Object.freeze({
  w: MOVEMENT_COMMANDS.UP,
  arrowup: MOVEMENT_COMMANDS.UP,
  s: MOVEMENT_COMMANDS.DOWN,
  arrowdown: MOVEMENT_COMMANDS.DOWN,
  a: MOVEMENT_COMMANDS.LEFT,
  arrowleft: MOVEMENT_COMMANDS.LEFT,
  d: MOVEMENT_COMMANDS.RIGHT,
  arrowright: MOVEMENT_COMMANDS.RIGHT
});

function draw() {
  if (!grid) return;

  const rows = grid.length;
  const cols = grid[0].length;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw tiles
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const tile = grid[y][x];
      ctx.fillStyle = tile === TILE_IDS.LAND ? "#228B22" : "#1E90FF";
      ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }
  }

  // Draw all players
  Object.entries(players).forEach(([sid, pos]) => {
    const spriteSrc = `assets/player/${pos.sprite}`;

    if (!spriteCache[spriteSrc]) {
      const img = new Image();
      img.src = spriteSrc;
      spriteCache[spriteSrc] = img;
    }

    const img = spriteCache[spriteSrc];

    if (img.complete) {
      ctx.drawImage(img, pos.x * TILE_SIZE, pos.y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }

    // Draw name tag
    ctx.fillStyle = "white";
    ctx.font = "10px 'Press Start 2P', monospace";
    ctx.textAlign = "center";
    ctx.fillText(pos.name, pos.x * TILE_SIZE + TILE_SIZE / 2, pos.y * TILE_SIZE + TILE_SIZE + 10);
  });
}

window.addEventListener("keydown", (e) => {
  // hides instructions
  hideWASDInstructionsAfterDelay();

  const key = e.key.toLowerCase();
  const direction = KEY_TO_DIRECTION[key] ?? null;

  if (direction) {
    socket.emit("move", { direction });
  }

  // plays music starting when you hit a key
  const music = document.getElementById("bgMusic");
  if (music && music.paused) {
    music.play().catch((error) => console.log("🎵 Autoplay blocked:", error));
  }
});

window.addEventListener("click", () => {});

let instructionsHidden = false;

function hideWASDInstructionsAfterDelay() {
  if (instructionsHidden) return;

  instructionsHidden = true;
  setTimeout(() => {
    const instructions = document.getElementById("instructions");
    if (instructions) {
      instructions.classList.add("hidden");
    }
  }, 1000); // 1 second
}
