// ------------------------------------------------------------------
//  Spieler-Logik: Zustand laden, übersetzen, Hilfen, Prüfen, Weiter
// ------------------------------------------------------------------
const token = localStorage.getItem("token");
if (!token) { window.location.href = "/"; }

let state = null;
let timerStart = null;       // Client-Timer (nur Anzeige)
let timerInterval = null;
let currentSentenceNumber = null;

// --- DOM ---
const $ = (id) => document.getElementById(id);
const els = {
  who: $("who"), progress: $("progress"), score: $("score"), timer: $("timer"),
  latin: $("latin"), freeTip: $("freeTip"), translation: $("translation"),
  help1Btn: $("help1Btn"), help2Btn: $("help2Btn"), checkBtn: $("checkBtn"),
  penaltyHint: $("penaltyHint"), feedbackArea: $("feedbackArea"),
  nextRow: $("nextRow"), nextBtn: $("nextBtn"),
  help1Panel: $("help1Panel"), vocabList: $("vocabList"), grammarList: $("grammarList"),
  help2Panel: $("help2Panel"), chat: $("chat"), chatInput: $("chatInput"),
  chatSend: $("chatSend"), chatHint: $("chatHint"),
  gameArea: $("gameArea"), endArea: $("endArea"),
  finalScore: $("finalScore"), finalMeta: $("finalMeta"),
  finalBoard: $("finalBoard"), toast: $("toast"),
  solutionOverlay: $("solutionOverlay"), solTitle: $("solTitle"),
  solLatin: $("solLatin"), solText: $("solText"), solContinue: $("solContinue"),
};

// True, solange das Musterlösungs-Zwischenmenü offen ist (pausiert den Hintergrund-Abgleich).
let overlayOpen = false;

function toast(msg) {
  els.toast.textContent = msg;
  els.toast.classList.add("show");
  setTimeout(() => els.toast.classList.remove("show"), 2500);
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

// --- Timer (reine Anzeige; die echte Zeit misst der Server) ---
function startTimer() {
  timerStart = Date.now();
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    const s = Math.floor((Date.now() - timerStart) / 1000);
    els.timer.textContent = s + "s";
  }, 250);
}
function stopTimer() { if (timerInterval) clearInterval(timerInterval); }

// --- Zustand laden ---
async function loadState() {
  const res = await fetch("/api/state?token=" + encodeURIComponent(token));
  if (res.status === 401) {
    stopTimer();
    alert("Deine Session wurde beendet (evtl. vom Admin entfernt).");
    localStorage.removeItem("token");
    window.location.href = "/";
    return;
  }
  state = await res.json();
  render();
}

function render() {
  els.who.textContent = "👤 " + state.nickname;
  els.score.textContent = state.total_score;

  if (state.status === "finished") { renderEnd(); return; }

  els.gameArea.classList.remove("hidden");
  els.endArea.classList.add("hidden");

  const s = state.sentence;
  els.progress.textContent = "Satz " + s.number + "/" + s.total;
  els.latin.textContent = s.latin;

  // Neuer Satz? -> Felder/Timer zurücksetzen
  if (currentSentenceNumber !== s.number) {
    currentSentenceNumber = s.number;
    els.translation.value = "";
    els.feedbackArea.innerHTML = "";
    els.nextRow.classList.add("hidden");
    els.help1Panel.classList.add("hidden");
    els.help2Panel.classList.add("hidden");
    els.chat.innerHTML = "";
    renderAssistantHistory();
    startTimer();
  }

  // Gratis-Tipp (z. B. Satz 2)
  if (s.free_tip) {
    els.freeTip.innerHTML = esc(s.free_tip);
    els.freeTip.classList.remove("hidden");
  } else {
    els.freeTip.classList.add("hidden");
  }

  // Hilfe-Button-Beschriftung mit Abzügen
  els.help1Btn.textContent = state.help1_used
    ? "📖 Hilfe 1 (bereits genutzt)"
    : `📖 Hilfe 1: Grammatik & Vokabeln (−${state.penalties.help1})`;
  const limitTxt = state.help2_max ? ` ${state.help2_questions}/${state.help2_max}` : "";
  els.help2Btn.textContent = `🤖 Hilfe 2: KI-Assistent (−${state.penalties.help2}/Frage)${limitTxt}`;

  els.penaltyHint.textContent =
    `Bestanden ab ${state.pass_threshold ?? 60}% Qualität. Schnell + ohne Hilfen = mehr Punkte.`;

  // Falls Satz bereits bestanden (z. B. nach Reload), Weiter-Button zeigen
  if (state.current_passed) {
    els.nextRow.classList.remove("hidden");
    els.checkBtn.disabled = true;
  } else {
    els.checkBtn.disabled = false;
  }
}

function renderAssistantHistory() {
  els.chat.innerHTML = "";
  (state.assistant_history || []).forEach((m) => addChatMsg(m.role, m.content));
}

// --- Hilfe 1 ---
els.help1Btn.addEventListener("click", async () => {
  els.help1Panel.classList.toggle("hidden");
  if (els.help1Panel.classList.contains("hidden")) return;
  const res = await fetch("/api/help1", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  const data = await res.json();
  if (!res.ok) { toast(data.detail || "Fehler"); return; }
  els.vocabList.innerHTML = data.vocab.map((v) => `<li>${esc(v)}</li>`).join("");
  els.grammarList.innerHTML = data.grammar.map((g) => `<li>${esc(g)}</li>`).join("");
  if (data.charged) { toast(`Hilfe 1 geöffnet: −${data.penalty} Punkte`); }
  loadState();
});

// --- Hilfe 2: Assistent ---
els.help2Btn.addEventListener("click", () => {
  els.help2Panel.classList.toggle("hidden");
  if (!els.help2Panel.classList.contains("hidden")) els.chatInput.focus();
});

function addChatMsg(role, content) {
  const div = document.createElement("div");
  div.className = "msg " + (role === "user" ? "user" : "assistant");
  div.textContent = content;
  els.chat.appendChild(div);
  els.chat.scrollTop = els.chat.scrollHeight;
}

async function sendQuestion() {
  const q = els.chatInput.value.trim();
  if (!q) return;
  if (state.help2_max && state.help2_questions >= state.help2_max) {
    toast("Fragenlimit für diesen Satz erreicht."); return;
  }
  els.chatInput.value = "";
  addChatMsg("user", q);
  els.chatSend.disabled = true;
  els.chatHint.textContent = "Assistent denkt nach…";
  try {
    const res = await fetch("/api/assistant", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, message: q }),
    });
    const data = await res.json();
    if (!res.ok) { toast(data.detail || "Fehler"); els.chatHint.textContent = ""; els.chatSend.disabled = false; return; }
    addChatMsg("assistant", data.reply);
    if (!data.error) {
      els.chatHint.textContent = `Frage gezählt: −${data.penalty} Punkte (insgesamt ${data.questions_asked} Frage(n) zu diesem Satz).`;
      loadState();
    } else {
      els.chatHint.textContent = "Antwort kam nicht durch – diese Frage wurde nicht berechnet.";
    }
  } catch (e) {
    els.chatHint.textContent = "Verbindungsfehler.";
  }
  els.chatSend.disabled = false;
}
els.chatSend.addEventListener("click", sendQuestion);
els.chatInput.addEventListener("keydown", (e) => { if (e.key === "Enter") sendQuestion(); });

// --- Prüfen ---
els.checkBtn.addEventListener("click", async () => {
  const translation = els.translation.value.trim();
  if (!translation) { toast("Bitte zuerst übersetzen."); return; }
  els.checkBtn.disabled = true;
  els.feedbackArea.innerHTML = `<div class="feedback warn">Übersetzung wird bewertet…</div>`;
  try {
    const res = await fetch("/api/check", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, translation }),
    });
    const data = await res.json();
    if (!res.ok) { els.feedbackArea.innerHTML = `<div class="feedback bad">${esc(data.detail || "Fehler")}</div>`; els.checkBtn.disabled = false; return; }
    renderFeedback(data);
  } catch (e) {
    els.feedbackArea.innerHTML = `<div class="feedback bad">Verbindungsfehler. Bitte erneut „Prüfen“.</div>`;
    els.checkBtn.disabled = false;
  }
});

function renderFeedback(data) {
  const cls = data.passed ? "ok" : "bad";
  let html = `<div class="feedback ${cls}">`;
  html += `<div class="quality-bar"><span style="width:${data.quality}%"></span></div>`;
  html += `<strong>Qualität: ${data.quality}%</strong> `;
  html += data.passed ? "✓ bestanden!" : `✗ noch nicht (ab ${data.pass_threshold}%).`;
  html += `<p>${esc(data.feedback)}</p>`;
  if (data.passed && data.breakdown) {
    const b = data.breakdown;
    html += `<p class="muted">Qualitätspunkte ${b.quality_points} + Zeitbonus ${b.time_bonus}`;
    if (b.help1_penalty) html += ` − Hilfe 1 ${b.help1_penalty}`;
    if (b.help2_penalty) html += ` − Assistent ${b.help2_penalty}`;
    if (b.retry_penalty) html += ` − Wiederholung ${b.retry_penalty}`;
    html += ` = <strong>${b.points} Punkte</strong></p>`;
  }
  html += `</div>`;
  els.feedbackArea.innerHTML = html;

  els.score.textContent = data.total_score;

  if (data.passed) {
    stopTimer();
    els.nextRow.classList.remove("hidden");
    els.checkBtn.disabled = true;
  } else {
    els.checkBtn.disabled = false;
  }
}

// --- Weiter ---
els.nextBtn.addEventListener("click", async () => {
  els.nextBtn.disabled = true;
  const res = await fetch("/api/next", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  const data = await res.json();
  els.nextBtn.disabled = false;
  if (!res.ok) { toast(data.detail || "Fehler"); return; }
  // Zwischenmenü mit der Musterübersetzung des gerade gelösten Satzes zeigen,
  // danach erst zum nächsten Satz (bzw. Endbildschirm) weiter.
  showSolutionInterstitial(data.completed, () => {
    state = data.state;
    render();
  });
});

// Zwischenmenü: zeigt die Musterübersetzung des abgeschlossenen Satzes.
function showSolutionInterstitial(completed, onContinue) {
  if (!completed) { onContinue(); return; }
  els.solTitle.textContent = `Satz ${completed.number} geschafft! ✓`;
  els.solLatin.textContent = completed.latin;
  els.solText.innerHTML = "<strong>Musterübersetzung:</strong> " + esc(completed.solution);
  overlayOpen = true;
  els.solutionOverlay.classList.remove("hidden");
  els.solContinue.onclick = () => {
    els.solutionOverlay.classList.add("hidden");
    overlayOpen = false;
    onContinue();
  };
}

function renderEnd() {
  stopTimer();
  els.gameArea.classList.add("hidden");
  els.endArea.classList.remove("hidden");
  els.finalScore.textContent = state.total_score + " Punkte";
  const board = state.leaderboard || [];
  const me = board.find((r) => r.nickname === state.nickname);
  const place = me ? me.rank : "–";
  els.finalMeta.textContent =
    `Gesamtzeit: ${Math.round(state.total_time_seconds)}s · Platz ${place} von ${board.length}`;
  els.finalBoard.innerHTML = board.map((r) => {
    const meCls = r.nickname === state.nickname ? ' class="me"' : "";
    return `<tr${meCls}><td class="rank r${r.rank}">${r.rank}</td><td>${esc(r.nickname)}</td>` +
           `<td>${r.total_score}</td><td>${Math.round(r.total_time_seconds)}s</td></tr>`;
  }).join("");
}

loadState();

// Leichter Hintergrund-Abgleich (alle 5s): erkennt, wenn der Admin das Team
// weiterschiebt, kickt oder das Spiel beendet. Greift NICHT ins Tippen/Prüfen ein
// – es wird nur neu gezeichnet, wenn sich Satznummer/Status tatsächlich ändern.
// Dieser Aufruf nutzt KEINE KI (nur /api/state), kostet also kein Limit.
setInterval(async () => {
  if (!state || overlayOpen) return;   // während des Zwischenmenüs nicht neu zeichnen
  try {
    const res = await fetch("/api/state?token=" + encodeURIComponent(token));
    if (res.status === 401) {
      stopTimer();
      alert("Deine Session wurde beendet (evtl. vom Admin entfernt).");
      localStorage.removeItem("token");
      window.location.href = "/";
      return;
    }
    const fresh = await res.json();
    const becameFinished = fresh.status === "finished" && state.status !== "finished";
    const sentenceChanged = fresh.sentence && state.sentence &&
                            fresh.sentence.number !== state.sentence.number;
    if (becameFinished || sentenceChanged) {
      state = fresh;
      render();
    }
  } catch (e) { /* Netzwerk-Hänger ignorieren */ }
}, 5000);
