"""
Zentrale Konfiguration für das Punktesystem und die KI.

>>> HIER kannst du gefahrlos alle Punktewerte anpassen. <<<

Alle Werte lassen sich zusätzlich per Umgebungsvariable überschreiben
(praktisch fürs Deployment), Default ist aber immer der hier gesetzte Wert.
"""
import os

# Lokal: Werte aus einer .env-Datei laden (im Deployment kommen sie aus der
# echten Umgebung; dann ist die .env meist nicht vorhanden, was unkritisch ist).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _int_env(name: str, default: int) -> int:
    """Liest eine Ganzzahl aus der Umgebung, fällt sonst auf den Default zurück."""
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# PUNKTESYSTEM  (siehe Abschnitt 5 der Aufgabenstellung)
# ---------------------------------------------------------------------------

# Grundpunkte pro Satz, werden mit der KI-Qualität (0..100 %) multipliziert.
BASE_POINTS_PER_SENTENCE = _int_env("BASE_POINTS_PER_SENTENCE", 100)

# Ab dieser KI-Qualität (in %) gilt ein Satz als bestanden -> Weitergehen erlaubt.
PASS_THRESHOLD = _int_env("PASS_THRESHOLD", 60)

# Zeitbonus: maximaler Bonus und Zielzeit (Sekunden) für vollen Bonus bei 0 s.
TIME_BONUS_MAX = _int_env("TIME_BONUS_MAX", 60)
TIME_TARGET_SECONDS = _int_env("TIME_TARGET_SECONDS", 180)

# Hilfe-Abzüge.
HELP1_PENALTY = _int_env("HELP1_PENALTY", 15)        # einmalig pro Satz beim 1. Öffnen
HELP2_PENALTY = _int_env("HELP2_PENALTY", 10)        # pro gestellter Assistenten-Frage
HELP2_MAX_QUESTIONS = _int_env("HELP2_MAX_QUESTIONS", 0)  # 0 = unbegrenzt

# Optionaler Abzug pro erneutem "Prüfen" (Wiederholung). Default 0.
RETRY_PENALTY = _int_env("RETRY_PENALTY", 0)


def compute_time_bonus(seconds: float) -> int:
    """Zeitbonus = max(0, round(MAX * (1 - sekunden / ZIEL)))."""
    if TIME_TARGET_SECONDS <= 0:
        return 0
    bonus = TIME_BONUS_MAX * (1 - seconds / TIME_TARGET_SECONDS)
    return max(0, round(bonus))


def compute_sentence_points(quality: int, seconds: float,
                            help1_used: bool, help2_questions: int,
                            retries: int) -> dict:
    """
    Berechnet die Punkte für einen Satz.

    Satzpunkte = Qualitätspunkte + Zeitbonus - Hilfe-Abzüge - Wiederholungs-Abzüge,
    nie unter 0.
    """
    quality_points = round(BASE_POINTS_PER_SENTENCE * (quality / 100))
    time_bonus = compute_time_bonus(seconds)
    help1_pen = HELP1_PENALTY if help1_used else 0
    help2_pen = HELP2_PENALTY * max(0, help2_questions)
    retry_pen = RETRY_PENALTY * max(0, retries)

    total = quality_points + time_bonus - help1_pen - help2_pen - retry_pen
    total = max(0, total)
    return {
        "quality_points": quality_points,
        "time_bonus": time_bonus,
        "help1_penalty": help1_pen,
        "help2_penalty": help2_pen,
        "retry_penalty": retry_pen,
        "points": total,
    }


# ---------------------------------------------------------------------------
# KI / GOOGLE GEMINI
# ---------------------------------------------------------------------------

# Modell für Bewertung und Assistent. Überschreibbar per GEMINI_MODEL.
# Im Gratis-Tarif verfügbar sind z. B. "gemini-2.5-flash" oder "gemini-2.0-flash".
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# Geheimnisse kommen AUSSCHLIESSLICH aus der Umgebung (nie hardcoden!).
# Gratis-Key erstellen unter: https://aistudio.google.com/apikey
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# Öffentliche Basis-URL für Beitritts-Link / QR-Code (z. B. https://meinegfs.onrender.com).
# Leer lassen -> die App leitet die URL aus dem eingehenden Request ab.
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")

# Pfad zur SQLite-Datei.
DB_PATH = os.environ.get("DB_PATH", "game.db")
