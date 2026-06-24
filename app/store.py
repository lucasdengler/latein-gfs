"""
Spielzustand: In-Memory-Modell mit SQLite-Write-Through (Backup).

Es gibt genau EIN laufendes Spiel (ein Raum) – passend für eine Schulstunde.
Bei einem Neustart des Servers wird der Zustand aus der SQLite-Datei geladen,
sodass ein Reload den Fortschritt der Spieler nicht verliert.

Wichtig: Die App läuft als EIN uvicorn-Prozess (siehe Procfile/Dockerfile),
deshalb genügt ein einfacher In-Memory-Store mit Lock.
"""
import secrets
import sqlite3
import threading
import time

from . import config
from .content import SENTENCE_COUNT

_lock = threading.RLock()


# ---------------------------------------------------------------------------
# Datenklassen (als einfache Dicts gehalten -> leicht (de)serialisierbar)
# ---------------------------------------------------------------------------

def _new_player(nickname: str) -> dict:
    now = time.time()
    return {
        "id": secrets.token_hex(8),
        "session_token": secrets.token_urlsafe(24),
        "nickname": nickname,
        "current_sentence_index": 0,
        "total_score": 0,
        "total_time_seconds": 0.0,
        "status": "playing",          # playing | finished | kicked
        "connected": True,
        "joined_at": now,
        "sentence_started_at": now,   # Startzeit des aktuellen Satzes
        "current_passed": False,      # aktueller Satz schon bestanden?
        "last_seen": now,
    }


class Store:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.players: dict[str, dict] = {}
        # SentenceRecord pro (player_id, sentence_index)
        self.records: dict[tuple[str, int], dict] = {}
        # Assistenten-Verlauf pro (player_id, sentence_index) -> Liste von Nachrichten
        self.assistant_history: dict[tuple[str, int], list[dict]] = {}
        self.game_created_at = time.time()
        self._init_db()
        self._load()

    # ----------------------------------------------------------- SQLite
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as c:
            c.execute(
                """CREATE TABLE IF NOT EXISTS players (
                    id TEXT PRIMARY KEY,
                    session_token TEXT,
                    nickname TEXT,
                    current_sentence_index INTEGER,
                    total_score INTEGER,
                    total_time_seconds REAL,
                    status TEXT,
                    joined_at REAL,
                    sentence_started_at REAL,
                    current_passed INTEGER
                )"""
            )
            c.execute(
                """CREATE TABLE IF NOT EXISTS records (
                    player_id TEXT,
                    sentence_index INTEGER,
                    time_seconds REAL,
                    help1_used INTEGER,
                    help2_questions INTEGER,
                    retries INTEGER,
                    quality INTEGER,
                    points INTEGER,
                    PRIMARY KEY (player_id, sentence_index)
                )"""
            )

    def _load(self):
        with self._conn() as c:
            for row in c.execute("SELECT * FROM players"):
                p = dict(row)
                p["current_passed"] = bool(p["current_passed"])
                p["connected"] = False
                p["last_seen"] = p["joined_at"]
                self.players[p["id"]] = p
            for row in c.execute("SELECT * FROM records"):
                r = dict(row)
                r["help1_used"] = bool(r["help1_used"])
                self.records[(r["player_id"], r["sentence_index"])] = r

    def _save_player(self, p: dict):
        with self._conn() as c:
            c.execute(
                """INSERT OR REPLACE INTO players
                (id, session_token, nickname, current_sentence_index, total_score,
                 total_time_seconds, status, joined_at, sentence_started_at, current_passed)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (p["id"], p["session_token"], p["nickname"], p["current_sentence_index"],
                 p["total_score"], p["total_time_seconds"], p["status"], p["joined_at"],
                 p["sentence_started_at"], int(p["current_passed"])),
            )

    def _save_record(self, r: dict):
        with self._conn() as c:
            c.execute(
                """INSERT OR REPLACE INTO records
                (player_id, sentence_index, time_seconds, help1_used, help2_questions,
                 retries, quality, points) VALUES (?,?,?,?,?,?,?,?)""",
                (r["player_id"], r["sentence_index"], r["time_seconds"],
                 int(r["help1_used"]), r["help2_questions"], r["retries"],
                 r["quality"], r["points"]),
            )

    def _delete_player_db(self, player_id: str):
        with self._conn() as c:
            c.execute("DELETE FROM players WHERE id=?", (player_id,))
            c.execute("DELETE FROM records WHERE player_id=?", (player_id,))

    # ----------------------------------------------------------- Records-Helfer
    def _record(self, player_id: str, idx: int) -> dict:
        key = (player_id, idx)
        if key not in self.records:
            self.records[key] = {
                "player_id": player_id,
                "sentence_index": idx,
                "time_seconds": 0.0,
                "help1_used": False,
                "help2_questions": 0,
                "retries": 0,
                "quality": 0,
                "points": 0,
            }
        return self.records[key]

    # ----------------------------------------------------------- öffentliche API
    def join(self, nickname: str) -> dict:
        with _lock:
            p = _new_player(nickname)
            self.players[p["id"]] = p
            self._save_player(p)
            return p

    def get_by_token(self, token: str) -> dict | None:
        if not token:
            return None
        for p in self.players.values():
            if p["session_token"] == token and p["status"] != "kicked":
                return p
        return None

    def get(self, player_id: str) -> dict | None:
        return self.players.get(player_id)

    def touch(self, p: dict, connected: bool = True):
        p["last_seen"] = time.time()
        p["connected"] = connected

    def mark_help1(self, p: dict) -> bool:
        """Markiert Hilfestufe 1 als genutzt. Gibt True zurück, wenn ERSTMALS
        (also Punktabzug fällig), sonst False."""
        with _lock:
            rec = self._record(p["id"], p["current_sentence_index"])
            if rec["help1_used"]:
                return False
            rec["help1_used"] = True
            self._save_record(rec)
            return True

    def add_assistant_question(self, p: dict) -> int:
        """Zählt eine Assistenten-Frage. Gibt die neue Frageanzahl für den Satz zurück."""
        with _lock:
            rec = self._record(p["id"], p["current_sentence_index"])
            rec["help2_questions"] += 1
            self._save_record(rec)
            return rec["help2_questions"]

    def get_assistant_history(self, p: dict) -> list[dict]:
        return self.assistant_history.get((p["id"], p["current_sentence_index"]), [])

    def append_assistant(self, p: dict, role: str, content: str):
        key = (p["id"], p["current_sentence_index"])
        self.assistant_history.setdefault(key, []).append({"role": role, "content": content})

    def record_check(self, p: dict, quality: int, passed: bool) -> dict:
        """
        Verbucht einen „Prüfen“-Versuch. Bei Nichtbestehen wird ein
        Wiederholungs-Versuch gezählt. Bei Bestehen werden Zeit + Punkte
        berechnet und gutgeschrieben.
        Gibt ein Detail-Dict mit der Punkteaufschlüsselung zurück.
        """
        with _lock:
            idx = p["current_sentence_index"]
            rec = self._record(p["id"], idx)
            elapsed = max(0.0, time.time() - p["sentence_started_at"])

            if not passed:
                rec["retries"] += 1
                rec["quality"] = max(rec["quality"], quality)
                self._save_record(rec)
                return {"passed": False, "quality": quality, "points": 0,
                        "elapsed": elapsed, "breakdown": None}

            # bestanden: Zeit & Punkte fixieren
            rec["time_seconds"] = elapsed
            rec["quality"] = quality
            breakdown = config.compute_sentence_points(
                quality=quality,
                seconds=elapsed,
                help1_used=rec["help1_used"],
                help2_questions=rec["help2_questions"],
                retries=rec["retries"],
            )
            rec["points"] = breakdown["points"]
            self._save_record(rec)

            # Spieler-Gesamtwerte neu summieren (idempotent).
            p["current_passed"] = True
            self._recompute_totals(p)
            self._save_player(p)
            return {"passed": True, "quality": quality, "points": breakdown["points"],
                    "elapsed": elapsed, "breakdown": breakdown}

    def _recompute_totals(self, p: dict):
        total_score = 0
        total_time = 0.0
        for (pid, _idx), rec in self.records.items():
            if pid == p["id"]:
                total_score += rec["points"]
                total_time += rec["time_seconds"]
        p["total_score"] = total_score
        p["total_time_seconds"] = total_time

    def advance(self, p: dict) -> bool:
        """Zum nächsten Satz weitergehen (nur wenn aktueller bestanden).
        Gibt True zurück, wenn das Spiel danach beendet ist."""
        with _lock:
            if not p["current_passed"]:
                return p["status"] == "finished"
            if p["current_sentence_index"] + 1 >= SENTENCE_COUNT:
                p["status"] = "finished"
                self._save_player(p)
                return True
            p["current_sentence_index"] += 1
            p["current_passed"] = False
            p["sentence_started_at"] = time.time()
            self._save_player(p)
            return False

    # ----------------------------------------------------------- Admin
    def rename(self, player_id: str, new_name: str) -> bool:
        with _lock:
            p = self.players.get(player_id)
            if not p:
                return False
            p["nickname"] = new_name
            self._save_player(p)
            return True

    def kick(self, player_id: str) -> bool:
        with _lock:
            p = self.players.get(player_id)
            if not p:
                return False
            p["status"] = "kicked"
            p["connected"] = False
            # Session entwerten, damit der Spieler aus der Runde fliegt.
            p["session_token"] = "kicked-" + secrets.token_hex(4)
            self._save_player(p)
            return True

    def reset(self):
        """Neue Runde: alle Spieler und Punkte löschen."""
        with _lock:
            self.players.clear()
            self.records.clear()
            self.assistant_history.clear()
            self.game_created_at = time.time()
            with self._conn() as c:
                c.execute("DELETE FROM players")
                c.execute("DELETE FROM records")

    # ----------------------------------------------------------- Sichten
    def leaderboard(self) -> list[dict]:
        """Rangliste, sortiert nach Punkten (absteigend), Tiebreak: Zeit (aufsteigend)."""
        with _lock:
            rows = []
            for p in self.players.values():
                if p["status"] == "kicked":
                    continue
                # genutzte Hilfen über alle Sätze aufsummieren
                help1_count = 0
                help2_count = 0
                for (pid, _idx), rec in self.records.items():
                    if pid == p["id"]:
                        help1_count += 1 if rec["help1_used"] else 0
                        help2_count += rec["help2_questions"]
                rows.append({
                    "id": p["id"],
                    "nickname": p["nickname"],
                    "current_sentence": min(p["current_sentence_index"] + 1, SENTENCE_COUNT),
                    "total_sentences": SENTENCE_COUNT,
                    "total_score": p["total_score"],
                    "total_time_seconds": round(p["total_time_seconds"], 1),
                    "status": p["status"],
                    "connected": p["connected"],
                    "help1_count": help1_count,
                    "help2_count": help2_count,
                })
            rows.sort(key=lambda r: (-r["total_score"], r["total_time_seconds"]))
            for i, r in enumerate(rows, start=1):
                r["rank"] = i
            return rows


# Globale Store-Instanz
store = Store(config.DB_PATH)
