const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const TILE_SIZE = 25;
let grid = null;
let player = { x: 0, y: 0 };
let players = {};
let starterOptions = {};
let starterSelectionActive = false;

const savedProgress = JSON.parse(localStorage.getItem("playerProgress") || "{}");
const savedParty = JSON.parse(localStorage.getItem("playerParty") || "[]");

const socket = io("http://localhost:8000", {
  auth: {
    name: localStorage.getItem("playerName"),
    sprite: localStorage.getItem("playerSprite"),
    progress: savedProgress,
    party: savedParty
  }
});

socket.on("state", (data) => {
  grid = data.grid;
  player = data.player;
  players = data.players;
  starterOptions = data.starter_options || {};

  if (player?.progress?.starter_chosen) {
    localStorage.setItem("playerProgress", JSON.stringify(player.progress));
    localStorage.setItem("playerParty", JSON.stringify(player.party || []));
  }

  const rows = grid.length;
  const cols = grid[0].length;

  canvas.width = cols * TILE_SIZE;
  canvas.height = rows * TILE_SIZE;

  draw();
});

socket.on("players_update", (data) => {
  players = data;
  player = players[socket.id] || player;
  draw();
});

socket.on("starter_selection_required", (data) => {
  starterOptions = data.options || starterOptions;
  showStarterModal(data.message || "Choose your starter Pokémon.");
});

socket.on("starter_selection_error", (data) => {
  const statusEl = document.getElementById("starterStatus");
  statusEl.textContent = data.message;
});

socket.on("starter_selected", (data) => {
  const progress = data.progress || {};
  const party = data.party || [];

  localStorage.setItem("playerProgress", JSON.stringify(progress));
  localStorage.setItem("playerParty", JSON.stringify(party));

  hideStarterModal();
});

const spriteCache = {};

function draw() {
  if (!grid) return;

  const rows = grid.length;
  const cols = grid[0].length;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const tile = grid[y][x];

      if (tile === "L") ctx.fillStyle = "#228B22";
      else if (tile === "W") ctx.fillStyle = "#1E90FF";
      else if (tile === "T") ctx.fillStyle = "#0f5a1f";
      else if (tile === "P") ctx.fillStyle = "#e8d9a8";
      else if (tile === "S") ctx.fillStyle = "#ffe066";
      else ctx.fillStyle = "#333";

      ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }
  }

  Object.entries(players).forEach(([sid, pos]) => {
    const spriteSrc = `assets/player/${pos.sprite}`;

    if (!spriteCache[spriteSrc]) {
      const img = new Image();
      img.src = spriteSrc;
      spriteCache[spriteSrc] = img;
    }

    const img = spriteCache[spriteSrc];

    if (img.complete) {
      ctx.drawImage(
        img,
        pos.x * TILE_SIZE,
        pos.y * TILE_SIZE,
        TILE_SIZE,
        TILE_SIZE
      );
    }

    ctx.fillStyle = "white";
    ctx.font = "10px 'Press Start 2P', monospace";
    ctx.textAlign = "center";
    ctx.fillText(
      pos.name,
      pos.x * TILE_SIZE + TILE_SIZE / 2,
      pos.y * TILE_SIZE + TILE_SIZE + 10
    );
  });
}

window.addEventListener("keydown", (e) => {
  hideWASDInstructionsAfterDelay();

  if (starterSelectionActive) {
    e.preventDefault();
    return;
  }

  const key = e.key.toLowerCase();
  let direction = null;

  if (key === "w" || key === "arrowup") direction = "up";
  else if (key === "s" || key === "arrowdown") direction = "down";
  else if (key === "a" || key === "arrowleft") direction = "left";
  else if (key === "d" || key === "arrowright") direction = "right";

  if (direction) {
    socket.emit("move", { direction });
  }

  const music = document.getElementById("bgMusic");
  if (music && music.paused) {
    music.play().catch((err) => console.log("🎵 Autoplay blocked:", err));
  }
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
  }, 1000);
}

function showStarterModal(message) {
  const overlay = document.getElementById("starterOverlay");
  const list = document.getElementById("starterChoices");
  const statusEl = document.getElementById("starterStatus");

  starterSelectionActive = true;
  statusEl.textContent = message;
  list.innerHTML = "";

  Object.entries(starterOptions).forEach(([key, starter]) => {
    const button = document.createElement("button");
    button.className = "starter-option";
    button.innerHTML = `
      <h3>${starter.species}</h3>
      <p>Lv ${starter.level}</p>
      <small>${starter.moves.join(" • ")}</small>
    `;
    button.addEventListener("click", () => {
      socket.emit("choose_starter", { starter: key });
    });
    list.appendChild(button);
  });

  overlay.classList.remove("hidden");
}

function hideStarterModal() {
  starterSelectionActive = false;
  const overlay = document.getElementById("starterOverlay");
  overlay.classList.add("hidden");
}
