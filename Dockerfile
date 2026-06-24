# Schlankes Image für die FastAPI-App.
FROM python:3.12-slim

WORKDIR /app

# Abhängigkeiten zuerst (besseres Layer-Caching).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App-Code.
COPY . .

# Render/Railway setzen die Portnummer per Umgebungsvariable $PORT.
# Lokal als Default 8000.
ENV PORT=8000
EXPOSE 8000

# Single-Worker (wichtig: In-Memory-State + WebSocket laufen in EINEM Prozess).
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
