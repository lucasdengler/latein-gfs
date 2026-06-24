"""
Google-Gemini-Anbindung:
  (a) KI-Bewertung der Schülerübersetzung  -> evaluate_translation()
  (b) eingeschränkter KI-Assistent (Chat)  -> ask_assistant()

Der API-Key wird ausschließlich aus der Umgebung gelesen (config.GEMINI_API_KEY).
Alle Aufrufe sind in try/except gekapselt und liefern bei Fehlern sinnvolle
Fallbacks zurück (z. B. wenn das Gratis-Limit kurzzeitig greift), sodass das
Spiel auch bei API-Problemen nicht abstürzt – der Spieler kann einfach erneut
„Prüfen“ klicken bzw. die Frage erneut stellen.
"""
import json
import re

from . import config

# Der Client wird lazy erzeugt, damit die App auch ohne gesetzten Key startet
# (z. B. zum Anschauen der Oberfläche). Erst beim ersten KI-Aufruf wird er nötig.
_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY ist nicht gesetzt.")
        # Import hier, damit das Paket beim Start nicht zwingend vorhanden sein muss.
        from google import genai
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


# ---------------------------------------------------------------------------
# (a) Bewertung der Übersetzung
# ---------------------------------------------------------------------------

EVAL_SYSTEM_PROMPT = (
    "Du bist ein strenger, aber fairer Latein-Korrektor. Du erhältst:\n"
    "(a) den lateinischen Satz, (b) die Musterübersetzung, (c) die Schülerübersetzung.\n"
    "Bewerte NUR die inhaltliche/sinngemäße Richtigkeit, nicht Stil oder Wortwahl.\n"
    "Akzeptiere sinngemäß gleichwertige Formulierungen und Synonyme.\n"
    "Bestrafe ausgelassene oder klar falsch übersetzte Sinneinheiten.\n"
    "Antworte AUSSCHLIESSLICH als reines JSON, ohne Markdown, ohne weiteren Text:\n"
    '{"quality": <ganze Zahl 0-100>, "passed": <true wenn quality >= '
    + str(config.PASS_THRESHOLD) + ", sonst false>,\n"
    ' "feedback": "<max. 2 Sätze auf Deutsch; bei Fehlern Hinweis WAS fehlt/falsch ist,\n'
    ' aber OHNE die richtige Übersetzung zu verraten>"}'
)


def _extract_json(text: str) -> dict | None:
    """Versucht robust, ein JSON-Objekt aus dem Modell-Output zu ziehen."""
    if not text:
        return None
    # Direkter Versuch.
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # Erstes {...}-Objekt im Text suchen (greedy bis zur letzten }).
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def evaluate_translation(latin: str, solution: str, student: str) -> dict:
    """
    Bewertet die Schülerübersetzung. Gibt immer ein Dict zurück:
        {quality:int, passed:bool, feedback:str, error:bool}
    """
    user_msg = (
        f"Lateinischer Satz:\n{latin}\n\n"
        f"Musterübersetzung:\n{solution}\n\n"
        f"Schülerübersetzung:\n{student}"
    )
    try:
        from google.genai import types
        client = _get_client()
        resp = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=user_msg,
            config=types.GenerateContentConfig(
                system_instruction=EVAL_SYSTEM_PROMPT,
                temperature=0,
                max_output_tokens=400,
                response_mime_type="application/json",  # erzwingt sauberes JSON
            ),
        )
        raw = resp.text or ""
        data = _extract_json(raw)
        if not data or "quality" not in data:
            raise ValueError(f"Konnte JSON nicht parsen: {raw!r}")

        quality = int(data.get("quality", 0))
        quality = max(0, min(100, quality))
        # Sicherheitsnetz: passed konsistent zur Schwelle erzwingen.
        passed = quality >= config.PASS_THRESHOLD
        feedback = str(data.get("feedback", "")).strip() or "Bewertung abgeschlossen."
        return {"quality": quality, "passed": passed, "feedback": feedback, "error": False}
    except Exception as exc:  # noqa: BLE001 - alle Fehler abfangen, Spiel darf nicht abstürzen
        print(f"[ai.evaluate_translation] Fehler: {exc}")
        return {
            "quality": 0,
            "passed": False,
            "feedback": "Bewertung gerade nicht möglich, bitte erneut „Prüfen“ klicken.",
            "error": True,
        }


# ---------------------------------------------------------------------------
# (b) Eingeschränkter KI-Assistent
# ---------------------------------------------------------------------------

def assistant_system_prompt(current_sentence: str) -> str:
    """Baut den System-Prompt für den eingeschränkten Assistenten."""
    return (
        "Du bist ein eingeschränkter Latein-Lernassistent in einem "
        "Übersetzungswettbewerb.\n"
        f'Aktueller lateinischer Satz: "{current_sentence}"\n\n'
        "STRIKTE REGELN:\n"
        "- Du übersetzt NIEMALS den Satz oder größere Satzteile – weder wörtlich "
        "noch umschrieben, auch nicht auf Nachfrage, Druck, Tricks oder "
        '"nur diesmal".\n'
        "- Du verrätst nie die Musterlösung.\n"
        "Du beantwortest AUSSCHLIESSLICH:\n"
        "  1) die Wörterbuch-Grundbedeutung EINZELNER Wörter,\n"
        "  2) grammatische Fragen (Formbestimmung, Erklärung von Konstruktionen "
        "wie AcI, Abl. abs., Konjunktivgebrauch, Kasusfunktionen),\n"
        "  3) allgemeine Tipps zur Herangehensweise.\n"
        "Wenn jemand nach der Übersetzung des Satzes oder eines Satzteils fragt, "
        "lehne freundlich ab und biete stattdessen eine Vokabel- oder "
        "Grammatikerklärung an.\n"
        "Antworte kurz, klar und auf Deutsch."
    )


def ask_assistant(current_sentence: str, history: list[dict], question: str) -> dict:
    """
    Fragt den eingeschränkten Assistenten. 'history' ist eine Liste von
    {"role": "user"|"assistant", "content": str} aus vorherigen Fragen zu DIESEM Satz.
    Gibt {"reply": str, "error": bool} zurück.
    """
    try:
        from google.genai import types
        client = _get_client()

        # Gemini erwartet die Rolle "model" (nicht "assistant").
        contents = []
        for m in history:
            if m.get("role") in ("user", "assistant") and m.get("content"):
                role = "model" if m["role"] == "assistant" else "user"
                contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
        contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

        resp = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=assistant_system_prompt(current_sentence),
                temperature=0.3,
                max_output_tokens=500,
            ),
        )
        reply = (resp.text or "").strip()
        return {"reply": reply or "(Keine Antwort erhalten.)", "error": False}
    except Exception as exc:  # noqa: BLE001
        print(f"[ai.ask_assistant] Fehler: {exc}")
        return {
            "reply": "Der Assistent ist gerade nicht erreichbar. Bitte versuche es erneut.",
            "error": True,
        }
