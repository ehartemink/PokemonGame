const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const TILE_SIZE = 25;
let grid = null;
let player = { x: 0, y: 0 };
let players = {};

const socket = io("http://localhost:8000");

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

function draw() {
  if (!grid) return;

  const rows = grid.length;
  const cols = grid[0].length;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const tile = grid[y][x];
      ctx.fillStyle = tile === "L" ? "#228B22" : "#1E90FF";
      ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }
  }

  // Draw all players
  Object.entries(players).forEach(([sid, pos]) => {
    ctx.fillStyle = sid === socket.id ? "#ffffff" : "#ff4444"; // You = white, others = red
    ctx.beginPath();
    ctx.arc(
      pos.x * TILE_SIZE + TILE_SIZE / 2,
      pos.y * TILE_SIZE + TILE_SIZE / 2,
      TILE_SIZE / 2.5,
      0,
      Math.PI * 2
    );
    ctx.fill();

      // Draw the name tag
      const name = "william"; // TODO: replace with actual name later
      ctx.fillStyle = "white";
      ctx.font = "10px 'Press Start 2P', monospace";
      ctx.textAlign = "center";
      ctx.fillText(
        name,
        pos.x * TILE_SIZE + TILE_SIZE / 2,
        pos.y * TILE_SIZE + TILE_SIZE + 10 // below the player; change to -4 for above
      );
  });

}

window.addEventListener("keydown", (e) => {
  // hides instructions
  hideWASDInstructionsAfterDelay();


  const key = e.key.toLowerCase();
  let direction = null;

  if (key === "w" || key === "arrowup") direction = "up";
  else if (key === "s" || key === "arrowdown") direction = "down";
  else if (key === "a" || key === "arrowleft") direction = "left";
  else if (key === "d" || key === "arrowright") direction = "right";

  if (direction) {
    socket.emit("move", { direction });
  }


  // plays music starting when you hit a key
  const music = document.getElementById("bgMusic");
  if (music && music.paused) {
    music.play().catch(e => console.log("🎵 Autoplay blocked:", e));
  }
});

window.addEventListener("click", () => {
});

let instructionsHidden = false;

function hideWASDInstructionsAfterDelay() {
  if (instructionsHidden) return;

  instructionsHidden = true;
  setTimeout(() => {
    const instructions = document.getElementById("instructions");
    if (instructions) {
      instructions.classList.add("hidden");
    }
  }, 1000); // 1 seconds
}
