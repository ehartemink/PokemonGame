const selectSound = new Audio("assets/sfx/select.wav");
selectSound.preload = "auto";

let selectedCharacter = null;

document.querySelectorAll(".char-option").forEach(option => {
  option.addEventListener("click", () => {
    document.querySelectorAll(".char-option").forEach(o => o.classList.remove("selected"));
    option.classList.add("selected");
    selectedCharacter = option.dataset.character;
    playSelectSound();
  });
});

function enterWorld() {
  playSelectSound();
  const name = document.getElementById("nameInput").value.trim();
  if (!name || !selectedCharacter) {
    alert("Please enter a name and select a character.");
    return;
  }

  localStorage.setItem("playerName", name);
  localStorage.setItem("playerSprite", selectedCharacter);
  // Redirect to game screen
  window.location.href = "world.html";

}

function playSelectSound() {
  selectSound.currentTime = 0; // rewind to start
  selectSound.play().catch((e) => {
    console.log("🔇 Sound blocked or failed:", e);
  });
}
