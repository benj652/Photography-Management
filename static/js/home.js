const API_PREFIX = "/api/v1";

async function updateStats() {
  // existing logic that fetches /items/all and updates stat cards
}

document.addEventListener("DOMContentLoaded", () => {
  updateStats();
  // optional: setInterval(updateStats, 60000);
});

document.getElementById("logoutButton").addEventListener("click", () => {
  window.location.href = "/auth/logout";
});
