let selectedCharacter = null;

document.querySelectorAll(".char-option").forEach(option => {
  option.addEventListener("click", () => {
    document.querySelectorAll(".char-option").forEach(o => o.classList.remove("selected"));
    option.classList.add("selected");
    selectedCharacter = option.dataset.character;
  });
});

function enterWorld() {
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
