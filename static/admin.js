// ------------------------------------------------------------------
//  Admin-Panel: Login, Live-Rangliste (WebSocket + Polling-Fallback),
//  Umbenennen, Kicken, Reset, QR/Link
// ------------------------------------------------------------------
const $ = (id) => document.getElementById(id);
let adminToken = localStorage.getItem("admin_token") || null;
let ws = null;
let pollTimer = null;

function toast(msg) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2500);
}
function esc(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

// --- Login ---
async function login() {
  const password = $("pw").value;
  $("loginErr").classList.add("hidden");
  try {
    const res = await fetch("/api/admin/login", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    const data = await res.json();
    if (!res.ok) { $("loginErr").textContent = data.detail || "Login fehlgeschlagen."; $("loginErr").classList.remove("hidden"); return; }
    adminToken = data.admin_token;
    localStorage.setItem("admin_token", adminToken);
    enterPanel();
  } catch (e) {
    $("loginErr").textContent = "Verbindungsfehler."; $("loginErr").classList.remove("hidden");
  }
}
$("loginBtn").addEventListener("click", login);
$("pw").addEventListener("keydown", (e) => { if (e.key === "Enter") login(); });

// --- Panel betreten ---
async function enterPanel() {
  // Erstabruf, prüft auch, ob der Token noch gültig ist.
  const ok = await refreshState();
  if (!ok) { adminToken = null; localStorage.removeItem("admin_token"); return; }
  $("loginCard").classList.add("hidden");
  $("panel").classList.remove("hidden");
  connectWS();
}

async function refreshState() {
  try {
    const res = await fetch("/api/admin/state?admin_token=" + encodeURIComponent(adminToken));
    if (res.status === 401) return false;
    const data = await res.json();
    $("joinLink").textContent = data.join_url;
    renderBoard(data.players);
    return true;
  } catch (e) { return false; }
}

// --- WebSocket Live-Updates ---
function connectWS() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/admin?admin_token=${encodeURIComponent(adminToken)}`);
  ws.onopen = () => { setLive(true); if (pollTimer) { clearInterval(pollTimer); pollTimer = null; } };
  ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    if (data.type === "leaderboard") renderBoard(data.players);
  };
  ws.onclose = () => { setLive(false); startPolling(); };
  ws.onerror = () => { setLive(false); };
}

function setLive(on) {
  $("liveDot").className = "status-dot " + (on ? "on" : "off");
  $("liveTxt").textContent = on ? "live (WebSocket)" : "Polling (2s)";
}

// Fallback: Polling alle 2 Sekunden, falls WebSocket nicht verfügbar.
function startPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(refreshState, 2000);
}

// --- Rangliste rendern ---
function renderBoard(players) {
  $("playerCount").textContent = `${players.length} Spieler in der Runde`;
  const body = $("board");
  if (!players.length) {
    body.innerHTML = `<tr><td colspan="8" class="muted center">Noch keine Spieler. Lass sie den QR-Code scannen!</td></tr>`;
    return;
  }
  body.innerHTML = players.map((p) => {
    const statusTxt = p.status === "finished" ? "fertig" : (p.connected ? "spielt" : "weg");
    const dot = p.status === "finished" ? "fin" : (p.connected ? "on" : "off");
    return `<tr>
      <td class="rank r${p.rank}">${p.rank}</td>
      <td><strong>${esc(p.nickname)}</strong></td>
      <td>${p.current_sentence}/${p.total_sentences}</td>
      <td><strong>${p.total_score}</strong></td>
      <td>${Math.round(p.total_time_seconds)}s</td>
      <td><span class="status-dot ${dot}"></span>${statusTxt}</td>
      <td class="muted">H1:${p.help1_count} · H2:${p.help2_count}</td>
      <td class="row" style="gap:6px">
        <button class="btn ghost small" onclick="renamePlayer('${p.id}','${esc(p.nickname)}')">Umbenennen</button>
        <button class="btn danger small" onclick="kickPlayer('${p.id}','${esc(p.nickname)}')">Kick</button>
      </td>
    </tr>`;
  }).join("");
}

// --- Aktionen ---
async function adminPost(path, payload) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Token": adminToken },
    body: JSON.stringify(payload || {}),
  });
  return res;
}

window.renamePlayer = async (id, current) => {
  const name = prompt("Neuer Name für „" + current + "“:", current);
  if (!name) return;
  const res = await adminPost("/api/admin/rename", { player_id: id, nickname: name });
  if (res.ok) { toast("Umbenannt."); refreshState(); }
  else { const d = await res.json(); toast(d.detail || "Fehler"); }
};

window.kickPlayer = async (id, name) => {
  if (!confirm(`„${name}“ wirklich aus der Runde entfernen?`)) return;
  const res = await adminPost("/api/admin/kick", { player_id: id });
  if (res.ok) { toast("Gekickt."); refreshState(); }
  else { const d = await res.json(); toast(d.detail || "Fehler"); }
};

$("resetBtn").addEventListener("click", async () => {
  if (!confirm("Neue Runde starten? ALLE Spieler und Punkte werden gelöscht.")) return;
  const res = await adminPost("/api/admin/reset", {});
  if (res.ok) { toast("Runde zurückgesetzt."); refreshState(); }
  else { toast("Fehler beim Zurücksetzen."); }
});

$("copyLink").addEventListener("click", () => {
  const link = $("joinLink").textContent;
  navigator.clipboard.writeText(link).then(() => toast("Link kopiert!"));
});

// --- Auto-Login, falls Token vorhanden ---
if (adminToken) { enterPanel(); }
