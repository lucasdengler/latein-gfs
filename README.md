# 🌋 Latein-GFS – Vesuv-Übersetzungswettbewerb

Eine gehostete, mehrspielerfähige Web-App für eine Latein-GFS. Mitschüler übersetzen
**Plinius, epistula 6,16,4–5** (Brief an Tacitus über den Vesuvausbruch) Satz für Satz
ins Deutsche – Kahoot-artig auf Zeit, mit Punktesystem, zwei Hilfestufen,
KI-gestützter Bewertung und einem Live-Admin-Panel mit Rangliste, Umbenennen und Kicken.

Die gesamte Oberfläche, alle KI-Antworten und alles Feedback sind auf **Deutsch**.

---

## Inhalt

- [Funktionen](#funktionen)
- [Architektur](#architektur)
- [Lokal starten](#lokal-starten)
- [Deployment auf Render.com](#deployment-auf-rendercom)
- [Deployment auf Railway](#deployment-auf-railway)
- [Umgebungsvariablen](#umgebungsvariablen)
- [Punktewerte & Inhalte anpassen](#punktewerte--inhalte-anpassen)
- [Spielablauf](#spielablauf)
- [Persistenz-Hinweis](#persistenz-hinweis)

---

## Funktionen

- **Beitritt per Link/QR** → Nickname eingeben → mitspielen.
- **4 lateinische Sätze** der Reihe nach (strikt sequenziell, ohne Bestehen kein Weiter).
- **KI-Bewertung** jeder Übersetzung (0–100 % Qualität, bestanden ab 60 %), Feedback ohne Lösungsverrat.
- **Hilfestufe 1** – statische Grammatik/Vokabeln (einmaliger Abzug pro Satz).
- **Hilfestufe 2** – eingeschränkter KI-Assistent, der **niemals** übersetzt (Abzug pro Frage).
- **Gratis-Tipp** bei Satz 2 (Datums-/„kal.“-Erklärung), automatisch ohne Abzug.
- **Punktesystem** mit Zeitbonus und Hilfe-Abzügen, Tiebreak über die Gesamtzeit.
- **Admin-Panel** (passwortgeschützt): permanent live aktualisierende Rangliste (WebSocket,
  Polling-Fallback), Spieler **umbenennen** und **kicken**, QR-Code + Link zum Beamen,
  „Neue Runde / Punkte zurücksetzen“.
- **Endbildschirm** mit Gesamtpunkten, Gesamtzeit, Platzierung und der Pinien-Metapher.

## Architektur

Ein einziger, einfach deploybarer Dienst:

| Teil            | Umsetzung                                                            |
|-----------------|---------------------------------------------------------------------|
| Backend+Frontend| **FastAPI** serviert HTML-Seiten *und* die JSON-API                  |
| Echtzeit        | **WebSocket** `/ws/admin` für die Live-Rangliste, Polling als Fallback |
| Persistenz      | **SQLite** (In-Memory-State mit Write-Through), Reload-fest          |
| KI              | **Google Gemini** (`google-genai`), Modell `gemini-2.5-flash`, Gratis-Tarif (Bewertung + Assistent)|
| QR-Code         | Python-Lib `qrcode`                                                  |

```
app/
  config.py     # >>> Punktewerte / KI-Einstellungen <<<
  content.py    # >>> Text, Musterübersetzung, Vokabeln, Grammatik, Gratis-Tipp <<<
  ai.py         # KI-Bewertung + eingeschränkter Assistent
  store.py      # Spielzustand + SQLite-Backup
  main.py       # Routen, WebSocket, QR
templates/      # join.html, play.html, admin.html
static/         # style.css, join.js, play.js, admin.js
```

> **Warum FastAPI statt Streamlit?** Streamlit wäre zwar noch einfacher zu hosten, ist aber
> für eine permanent live aktualisierende Multi-User-Rangliste, das Kicken/Umbenennen und
> echte WebSocket-Updates deutlich schwächer. Daher der FastAPI-Weg.

---

## Lokal starten

Voraussetzung: **Python 3.11+**.

```bash
# 1) ins Projektverzeichnis wechseln
cd Latein_GFS

# 2) virtuelle Umgebung anlegen + aktivieren
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 3) Abhängigkeiten installieren
pip install -r requirements.txt

# 4) Umgebungsvariablen setzen: .env aus Vorlage erstellen und ausfüllen
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
#   -> GEMINI_API_KEY und ADMIN_PASSWORD eintragen

# 5) starten
uvicorn app.main:app --reload
```

Dann im Browser öffnen:

- **Spieler / Beitritt:** <http://localhost:8000/>
- **Admin-Panel:** <http://localhost:8000/admin>  (Login mit deinem `ADMIN_PASSWORD`)

Im Admin-Panel erscheinen oben links **QR-Code und Beitritts-Link** – die kannst du
an die Wand beamen. Lokal nutzen Mitschüler im selben WLAN deine LAN-IP
(z. B. `http://192.168.x.y:8000/`); setze dafür `PUBLIC_BASE_URL` entsprechend,
damit QR/Link stimmen, und starte mit `--host 0.0.0.0`.

---

## Deployment auf Render.com

**Schritt für Schritt:**

1. **GitHub-Repo anlegen** und dieses Projekt hineinpushen:
   ```bash
   git init
   git add .
   git commit -m "Latein-GFS Web-App"
   git branch -M main
   git remote add origin https://github.com/DEINNAME/latein-gfs.git
   git push -u origin main
   ```
   (Die `.gitignore` sorgt dafür, dass `.env` und `*.db` **nicht** hochgeladen werden.)

2. Auf <https://dashboard.render.com> einloggen → **New** → **Blueprint** →
   dein Repo auswählen. Render liest die mitgelieferte `render.yaml` und legt den
   Web-Service automatisch an. *(Alternativ: **New → Web Service**, „Python“,
   Build `pip install -r requirements.txt`, Start
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.)*

3. **Env-Vars setzen** (Service → *Environment*):
   - `GEMINI_API_KEY` = dein Google-Gemini-Key (gratis: https://aistudio.google.com/apikey)
   - `ADMIN_PASSWORD` = dein Wunschpasswort
   - `PUBLIC_BASE_URL` = die Render-URL, z. B. `https://latein-gfs.onrender.com`
     (erst nach dem ersten Deploy bekannt – dann eintragen & erneut deployen,
     damit QR/Link korrekt sind)

4. **Deploy** abwarten. Danach:
   - Spieler-Seite: `https://<dein-service>.onrender.com/`
   - Admin-Panel:   `https://<dein-service>.onrender.com/admin`

5. Im Admin-Panel findest du **QR-Code + Link** prominent zum Beamen.

> Tipp: Der Free-Tier „schläft“ nach Inaktivität ein und braucht beim ersten Aufruf
> einige Sekunden. Ruf die Seite **kurz vor der Stunde** einmal auf, damit der Dienst wach ist.

## Deployment auf Railway

1. Repo wie oben pushen.
2. <https://railway.app> → **New Project** → **Deploy from GitHub repo**.
3. Railway erkennt das `Dockerfile` (oder das `Procfile`) automatisch.
4. Unter **Variables** dieselben Env-Vars setzen (`GEMINI_API_KEY`, `ADMIN_PASSWORD`,
   `PUBLIC_BASE_URL`).
5. Unter **Settings → Networking** eine öffentliche Domain erzeugen → diese als
   `PUBLIC_BASE_URL` eintragen.

---

## Umgebungsvariablen

| Variable             | Pflicht | Bedeutung                                                        |
|----------------------|:------:|------------------------------------------------------------------|
| `GEMINI_API_KEY`     |  ✅    | Google-Gemini-Key (gratis: https://aistudio.google.com/apikey)   |
| `ADMIN_PASSWORD`     |  ✅    | Passwort fürs Admin-Panel                                        |
| `PUBLIC_BASE_URL`    |  –     | Öffentliche URL für QR/Link (sonst aus dem Request abgeleitet)   |
| `GEMINI_MODEL`       |  –     | Modell, Default `gemini-2.5-flash` (Alternative: `gemini-2.0-flash`) |
| `DB_PATH`            |  –     | Pfad der SQLite-Datei, Default `game.db`                         |
| diverse Punktewerte  |  –     | siehe `app/config.py` (alle per Env überschreibbar)             |

> **Sicherheit:** API-Key und Admin-Passwort werden **ausschließlich** aus der Umgebung
> gelesen – niemals im Code hardcoden. Lokal stehen sie in `.env` (nicht eingecheckt).

---

## Punktewerte & Inhalte anpassen

- **Punkte / Schwellen / Abzüge:** [`app/config.py`](app/config.py) – jede Zahl ist
  kommentiert und zusätzlich per Env-Var überschreibbar:
  `BASE_POINTS_PER_SENTENCE` (100), `PASS_THRESHOLD` (60),
  `TIME_BONUS_MAX` (60), `TIME_TARGET_SECONDS` (180),
  `HELP1_PENALTY` (15), `HELP2_PENALTY` (10), `HELP2_MAX_QUESTIONS` (1 pro Satz; 0 = unbegrenzt),
  `RETRY_PENALTY` (0).
- **Text, Musterübersetzung, Vokabeln, Grammatik, Gratis-Tipp:**
  [`app/content.py`](app/content.py). Die Anzahl spielbarer Sätze ergibt sich
  **automatisch** aus der Liste `SENTENCES` (die Anzeige „Satz X/N“ passt sich an).
  Möchtest du z. B. einen 5. Satz, füge einfach ein weiteres Dict hinzu.

> **Hinweis zur Satzanzahl:** Laut Vorlage gibt es „5 Sinn-Sätze“, davon sind **4 spielbar**
> (Sätze 1–4); der didaktische Schluss zur Pinien-Metapher wird als Text auf dem
> Endbildschirm gezeigt (`FINAL_NOTE`).

---

## Spielablauf

1. Link/QR öffnen → Nickname → beitreten.
2. Pro Satz: lateinischer Satz + Timer → Übersetzung tippen → optional Hilfe 1/2 →
   **Prüfen**. Ab 60 % Qualität bestanden → Punkte + **Weiter**. Sonst Feedback
   (ohne Lösung) und erneut versuchen.
3. Bei Satz 2 erscheint automatisch der **Gratis-Tipp** zu „Nonum kal.“ (ohne Abzug).
4. Nach Satz 4: Endbildschirm mit Punkten, Zeit, Platzierung und Pinien-Metapher.

**Punkte pro Satz** = Qualitätspunkte (`BASE × Qualität/100`) + Zeitbonus
− Hilfe-Abzüge − Wiederholungs-Abzüge, nie unter 0. Gesamt = Summe; Gleichstand →
kürzere Gesamtzeit gewinnt.

---

## Persistenz-Hinweis

Der Spielzustand liegt in SQLite (`game.db`) und übersteht einen Server-Reload.
**Auf dem kostenlosen Render-Tier ist die Festplatte aber flüchtig** – bei einem
Neu-Deploy oder dem Aufwachen aus dem Ruhezustand kann die Datei verloren gehen.
Für eine einzelne Schulstunde ist das unkritisch.

Optional **persistentes Volume** (überlebt Neustarts):
in `render.yaml` den auskommentierten `disk:`-Block aktivieren und zusätzlich
`DB_PATH=/var/data/game.db` setzen (persistente Volumes sind ggf. nur in
kostenpflichtigen Tiers verfügbar).
