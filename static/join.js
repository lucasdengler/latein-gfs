// Beitritts-Seite: Nickname absenden, Token speichern, zur Spielseite wechseln.
const nick = document.getElementById("nick");
const joinBtn = document.getElementById("joinBtn");
const err = document.getElementById("err");

// Falls schon eine gültige Session existiert -> direkt weiterspielen.
if (localStorage.getItem("token")) {
  // Wir prüfen serverseitig erst auf der Spielseite; hier nur Komfort-Hinweis.
}

function showError(msg) {
  err.textContent = msg;
  err.classList.remove("hidden");
}

async function join() {
  const nickname = nick.value.trim();
  if (!nickname) { showError("Bitte gib einen Nickname ein."); return; }
  joinBtn.disabled = true;
  err.classList.add("hidden");
  try {
    const res = await fetch("/api/join", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nickname }),
    });
    const data = await res.json();
    if (!res.ok) { showError(data.detail || "Beitritt fehlgeschlagen."); joinBtn.disabled = false; return; }
    localStorage.setItem("token", data.token);
    localStorage.setItem("nickname", data.nickname);
    window.location.href = "/play";
  } catch (e) {
    showError("Verbindungsfehler. Bitte erneut versuchen.");
    joinBtn.disabled = false;
  }
}

joinBtn.addEventListener("click", join);
nick.addEventListener("keydown", (e) => { if (e.key === "Enter") join(); });
