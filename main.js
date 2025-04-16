<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");

  const TILE_SIZE = 20;

  let grid = [];
  let player = { x: 0, y: 0 };

  const socket = io("http://localhost:8000");

  socket.on("state", (data) => {
    grid = data.grid;
    player = data.player;

    // Dynamically resize canvas based on grid size
    canvas.width = grid[0].length * TILE_SIZE;
    canvas.height = grid.length * TILE_SIZE;

    draw();
  });

  socket.on("player_update", (data) => {
    player = data.player;
    draw();
  });

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const rows = grid.length;
    const cols = grid[0].length;

    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const tile = grid[y][x];
        ctx.fillStyle = tile === "L" ? "#228B22" : "#1E90FF";
        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
      }
    }

    // Draw player
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(
      player.x * TILE_SIZE + TILE_SIZE / 2,
      player.y * TILE_SIZE + TILE_SIZE / 2,
      TILE_SIZE / 2.5,
      0,
      Math.PI * 2
    );
    ctx.fill();
  }

  window.addEventListener("keydown", (e) => {
    const key = e.key.toLowerCase();
    let direction = null;

    if (key === "w" || key === "arrowup") direction = "up";
    else if (key === "s" || key === "arrowdown") direction = "down";
    else if (key === "a" || key === "arrowleft") direction = "left";
    else if (key === "d" || key === "arrowright") direction = "right";

    if (direction) {
      socket.emit("move", { direction });
    }
  });
</script>
