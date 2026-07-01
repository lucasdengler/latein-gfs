"""
FastAPI-App: serviert die Seiten (Beitritt, Spieler, Admin) und die API,
inklusive WebSocket für die Live-Rangliste und QR-Code für den Beitritts-Link.

Start lokal:   uvicorn app.main:app --reload
"""
import asyncio
import html
import io
import re
import secrets

import qrcode
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import ai, config
from .content import FINAL_NOTE, SENTENCE_COUNT, help1_content, public_sentence
from .store import store

app = FastAPI(title="Latein-GFS – Vesuv-Übersetzungswettbewerb")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Gültige Admin-Session-Token (in-memory).
_admin_tokens: set[str] = set()


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def sanitize_nickname(raw: str) -> str:
    """Säubert Nicknames: HTML entschärfen, Länge begrenzen, Whitespace normalisieren."""
    raw = (raw or "").strip()
    raw = re.sub(r"\s+", " ", raw)
    raw = html.escape(raw)          # gegen HTML-Injection
    return raw[:24]


def base_url(request: Request) -> str:
    """Öffentliche Basis-URL für Links/QR. PUBLIC_BASE_URL hat Vorrang."""
    if config.PUBLIC_BASE_URL:
        return config.PUBLIC_BASE_URL
    return str(request.base_url).rstrip("/")


def require_admin(request: Request):
    """Prüft den Admin-Token aus Header oder Query. Wirft 401 bei Fehler."""
    token = request.headers.get("X-Admin-Token") or request.query_params.get("admin_token")
    if not token or token not in _admin_tokens:
        raise HTTPException(status_code=401, detail="Admin-Login erforderlich.")
    return token


def player_state_payload(p: dict) -> dict:
    """Baut die für den Spieler sichtbare Zustandsbeschreibung."""
    idx = p["current_sentence_index"]
    rec = store.records.get((p["id"], idx))
    payload = {
        "nickname": p["nickname"],
        "status": p["status"],
        "total_score": p["total_score"],
        "total_time_seconds": round(p["total_time_seconds"], 1),
        "current_passed": p["current_passed"],
        "help1_used": bool(rec and rec["help1_used"]),
        "help2_questions": rec["help2_questions"] if rec else 0,
        "help2_max": config.HELP2_MAX_QUESTIONS,
        "penalties": {
            "help1": config.HELP1_PENALTY,
            "help2": config.HELP2_PENALTY,
        },
    }
    if p["status"] == "finished":
        payload["sentence"] = None
        payload["final_note"] = FINAL_NOTE
        payload["leaderboard"] = store.leaderboard()
    else:
        payload["sentence"] = public_sentence(idx)
        payload["assistant_history"] = store.get_assistant_history(p)
    return payload


# ---------------------------------------------------------------------------
# WebSocket-Verwaltung (Live-Rangliste fürs Admin-Panel)
# ---------------------------------------------------------------------------

class AdminHub:
    def __init__(self):
        self.connections: set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.add(ws)

    def disconnect(self, ws: WebSocket):
        self.connections.discard(ws)

    async def broadcast(self):
        data = {"type": "leaderboard", "players": store.leaderboard()}
        dead = []
        for ws in list(self.connections):
            try:
                await ws.send_json(data)
            except Exception:  # noqa: BLE001
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


hub = AdminHub()


async def notify_admins():
    """Live-Rangliste an alle verbundenen Admin-Panels pushen."""
    await hub.broadcast()


# ---------------------------------------------------------------------------
# Seiten (HTML)
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def page_join(request: Request):
    return templates.TemplateResponse("join.html", {"request": request})


@app.get("/play", response_class=HTMLResponse)
async def page_play(request: Request):
    return templates.TemplateResponse("play.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def page_admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


# ---------------------------------------------------------------------------
# Spieler-API
# ---------------------------------------------------------------------------

@app.post("/api/join")
async def api_join(payload: dict):
    nickname = sanitize_nickname(payload.get("nickname", ""))
    if not nickname:
        raise HTTPException(status_code=400, detail="Bitte einen Nickname eingeben.")
    p = store.join(nickname)
    await notify_admins()
    return {"token": p["session_token"], "player_id": p["id"], "nickname": p["nickname"]}


def _auth_player(token: str) -> dict:
    p = store.get_by_token(token)
    if not p:
        raise HTTPException(status_code=401, detail="Session ungültig oder beendet.")
    store.touch(p, connected=True)
    return p


@app.get("/api/state")
async def api_state(token: str):
    p = _auth_player(token)
    return player_state_payload(p)


@app.post("/api/help1")
async def api_help1(payload: dict):
    p = _auth_player(payload.get("token", ""))
    if p["status"] != "playing":
        raise HTTPException(status_code=400, detail="Spiel ist beendet.")
    charged = store.mark_help1(p)   # True, wenn erstmals -> Punktabzug
    await notify_admins()
    content = help1_content(p["current_sentence_index"])
    return {
        "vocab": content["vocab"],
        "grammar": content["grammar"],
        "charged": charged,
        "penalty": config.HELP1_PENALTY if charged else 0,
    }


@app.post("/api/assistant")
async def api_assistant(payload: dict):
    p = _auth_player(payload.get("token", ""))
    if p["status"] != "playing":
        raise HTTPException(status_code=400, detail="Spiel ist beendet.")
    question = (payload.get("message", "") or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Leere Frage.")

    # optionales Frage-Limit pro Satz
    rec = store.records.get((p["id"], p["current_sentence_index"]))
    asked = rec["help2_questions"] if rec else 0
    if config.HELP2_MAX_QUESTIONS and asked >= config.HELP2_MAX_QUESTIONS:
        raise HTTPException(status_code=429,
                            detail=f"Fragenlimit für diesen Satz erreicht "
                                   f"({config.HELP2_MAX_QUESTIONS}).")

    idx = p["current_sentence_index"]
    latin = public_sentence(idx)["latin"]
    history = list(store.get_assistant_history(p))

    # KI-Aufruf nicht-blockierend ausführen.
    result = await asyncio.to_thread(ai.ask_assistant, latin, history, question)

    # Frage zählen (Punktabzug) und Verlauf speichern – nur bei erfolgreicher Antwort.
    new_count = asked
    if not result["error"]:
        store.append_assistant(p, "user", question)
        store.append_assistant(p, "assistant", result["reply"])
        new_count = store.add_assistant_question(p)
        await notify_admins()

    return {
        "reply": result["reply"],
        "error": result["error"],
        "questions_asked": new_count,
        "penalty": config.HELP2_PENALTY if not result["error"] else 0,
    }


@app.post("/api/check")
async def api_check(payload: dict):
    from .content import SENTENCES
    p = _auth_player(payload.get("token", ""))
    if p["status"] != "playing":
        raise HTTPException(status_code=400, detail="Spiel ist beendet.")
    translation = (payload.get("translation", "") or "").strip()
    if not translation:
        raise HTTPException(status_code=400, detail="Bitte zuerst eine Übersetzung eingeben.")

    idx = p["current_sentence_index"]
    s = SENTENCES[idx]
    result = await asyncio.to_thread(
        ai.evaluate_translation, s["latin"], s["solution"], translation
    )

    detail = store.record_check(p, result["quality"], result["passed"])
    await notify_admins()

    return {
        "quality": result["quality"],
        "passed": result["passed"],
        "feedback": result["feedback"],
        "error": result["error"],
        "points": detail["points"],
        "breakdown": detail["breakdown"],
        "total_score": p["total_score"],
        "pass_threshold": config.PASS_THRESHOLD,
    }


@app.post("/api/next")
async def api_next(payload: dict):
    from .content import SENTENCES
    p = _auth_player(payload.get("token", ""))
    if not p["current_passed"]:
        raise HTTPException(status_code=400,
                            detail="Aktueller Satz noch nicht bestanden.")
    # Musterlösung des gerade abgeschlossenen Satzes -> fürs Zwischenmenü.
    # Wird ERST NACH dem Bestehen ausgeliefert (nie vorher) – kein Schummel-Risiko.
    completed_idx = p["current_sentence_index"]
    completed = {
        "number": completed_idx + 1,
        "latin": SENTENCES[completed_idx]["latin"],
        "solution": SENTENCES[completed_idx]["solution"],
    }
    finished = store.advance(p)
    await notify_admins()
    return {"finished": finished, "state": player_state_payload(p), "completed": completed}


# ---------------------------------------------------------------------------
# Admin-API
# ---------------------------------------------------------------------------

@app.post("/api/admin/login")
async def api_admin_login(payload: dict):
    if not config.ADMIN_PASSWORD:
        raise HTTPException(status_code=500,
                            detail="ADMIN_PASSWORD ist auf dem Server nicht gesetzt.")
    if payload.get("password", "") != config.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Falsches Passwort.")
    token = secrets.token_urlsafe(24)
    _admin_tokens.add(token)
    return {"admin_token": token}


@app.get("/api/admin/state")
async def api_admin_state(request: Request):
    require_admin(request)
    return {
        "players": store.leaderboard(),
        "join_url": base_url(request) + "/",
        "sentence_count": SENTENCE_COUNT,
    }


@app.post("/api/admin/rename")
async def api_admin_rename(request: Request, payload: dict):
    require_admin(request)
    new_name = sanitize_nickname(payload.get("nickname", ""))
    if not new_name:
        raise HTTPException(status_code=400, detail="Leerer Name.")
    if not store.rename(payload.get("player_id", ""), new_name):
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden.")
    await notify_admins()
    return {"ok": True}


@app.post("/api/admin/kick")
async def api_admin_kick(request: Request, payload: dict):
    require_admin(request)
    if not store.kick(payload.get("player_id", "")):
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden.")
    await notify_admins()
    return {"ok": True}


@app.post("/api/admin/advance")
async def api_admin_advance(request: Request, payload: dict):
    """Not-Knopf: ein steckengebliebenes Team zum nächsten Satz schieben –
    entweder ohne Punkte (award_full=False) oder mit voller Punktzahl (award_full=True)."""
    require_admin(request)
    award_full = bool(payload.get("award_full", False))
    result = store.admin_advance(payload.get("player_id", ""), award_full)
    if result is None:
        raise HTTPException(status_code=404,
                            detail="Team nicht gefunden oder bereits fertig.")
    await notify_admins()
    return {"ok": True, "finished": result == "finished"}


@app.post("/api/admin/reset")
async def api_admin_reset(request: Request):
    require_admin(request)
    store.reset()
    await notify_admins()
    return {"ok": True}


# ---------------------------------------------------------------------------
# QR-Code für den Beitritts-Link
# ---------------------------------------------------------------------------

@app.get("/qr")
async def qr_code(request: Request):
    url = base_url(request) + "/"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


# ---------------------------------------------------------------------------
# WebSocket: Live-Rangliste fürs Admin-Panel
# ---------------------------------------------------------------------------

@app.websocket("/ws/admin")
async def ws_admin(websocket: WebSocket):
    token = websocket.query_params.get("admin_token")
    if not token or token not in _admin_tokens:
        await websocket.close(code=4401)
        return
    await hub.connect(websocket)
    try:
        # initiale Rangliste senden
        await websocket.send_json({"type": "leaderboard", "players": store.leaderboard()})
        while True:
            # Wir erwarten keine Nachrichten vom Client; halten die Verbindung offen.
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
    except Exception:  # noqa: BLE001
        hub.disconnect(websocket)


@app.get("/healthz")
async def healthz():
    return JSONResponse({"status": "ok", "gemini_key_set": bool(config.GEMINI_API_KEY)})
