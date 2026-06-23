# Blackpool Assessment — AI REST API

REST API built with **FastAPI** integrating **Azure OpenAI** (document analysis) and **Deepgram** (speech-to-text / text-to-speech), backed by **PostgreSQL** for request tracking.

The project ships with a full **interactive web UI** — no Swagger needed. Open `http://localhost:8000` after launching.

---

## Prerequisites

### Windows users — do this FIRST (one-time setup)

Before installing Docker Desktop, you must enable WSL 2 (Windows Subsystem for Linux). Docker Desktop on Windows requires it.

**Step 1 — Open PowerShell as Administrator and run:**
```powershell
wsl --install
```
**Step 2 — Restart your computer when prompted.**

> If WSL is already installed, this command does nothing. It is safe to run again.

---

### All platforms

| Requirement | Version | Notes |
|------------|---------|-------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 4.0+ | **Required** — handles Python, PostgreSQL, everything |
| Git | any | To clone the repo |

> Docker Desktop must be **running** (whale icon visible in system tray / menu bar) before you launch the project. Everything else — Python, dependencies, database — is handled automatically inside containers.

---

## Quick Start

> ⚠️ **All commands must be run from the repository root** (`ai-technical-assessment/`).  
> Do NOT `cd` into any subfolder before running `docker compose`.

### Option A — Double-click launcher (Windows)

1. Complete the WSL 2 setup above
2. Clone the repo and open its folder
3. Copy `.env.example` → `.env` and fill in your API keys
4. Double-click **`start.bat`**

The script checks Docker, sets up the environment, builds the containers, waits for the API to be healthy, and opens your browser automatically.

---

### Option B — Manual (any OS)

```bash
# 1. Clone and enter the repository root
git clone https://github.com/UrsaMinoR3/ai-technical-assessment.git
cd ai-technical-assessment

# 2. Set up credentials  ← stay in this directory
cp .env.example .env
# Open .env and fill in your API keys (see table below)

# 3. Launch  ← run from repository root, NOT from any subfolder
docker compose up --build
```

**Mac / Linux — use the shell launcher instead:**
```bash
chmod +x start.sh
./start.sh
```

---

## URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | **Interactive Web UI** (main entry point) |
| `http://localhost:8000/docs` | Swagger / OpenAPI reference |
| `http://localhost:8000/health` | Health check (no auth required) |

**API Key** (pre-set in `.env.example`): `blackpool-architect-key-2024`

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description |
|----------|-------------|
| `DB_USER` | PostgreSQL username (default: `postgres`) |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_NAME` | Database name (default: `ai_assessment`) |
| `API_KEY` | Internal API key — sent as `X-API-Key` header on every request |
| `AZURE_OPENAI_KEY` | Azure OpenAI (or OpenAI) API key |
| `AZURE_OPENAI_BASE_URL` | API base URL (e.g. `https://your-resource.openai.azure.com/openai/v1/`) |
| `AZURE_OPENAI_MODEL` | Model name (e.g. `gpt-4o`) |
| `DEEPGRAM_API_KEY` | Deepgram API key |

> **Security:** `.env` is listed in `.gitignore` — real credentials are never committed to the repository. CI/CD uses GitHub Secrets.

---

## Endpoints

All endpoints except `/health` require the `X-API-Key` header.

### `POST /stt` — Speech-to-Text
Transcribes an MP3 or WAV file using **Deepgram Nova-2** with speaker diarization and auto language detection.

```bash
curl -X POST http://localhost:8000/stt \
  -H "X-API-Key: blackpool-architect-key-2024" \
  -F "audio=@recording.mp3"
```

**Response:**
```json
{
  "transcript": "Hola, ¿cómo estás hoy?",
  "language": "es",
  "duration": 3.42,
  "speakers": [
    { "speaker": 0, "start": 0.0, "end": 3.42, "text": "Hola, ¿cómo estás hoy?" }
  ]
}
```

---

### `POST /tts` — Text-to-Speech
Synthesizes text to a downloadable MP3 using **Deepgram Aura-2** (80+ voices, 7 languages).

```bash
curl -X POST http://localhost:8000/tts \
  -H "X-API-Key: blackpool-architect-key-2024" \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome to Blackpool.", "voice": "aura-2-asteria-en"}' \
  --output speech.mp3
```

Available language codes: `en`, `es`, `de`, `nl`, `it`, `fr`, `ja`

---

### `POST /idp/analyze` — Intelligent Document Processing
Extracts structured fields from a document image using **Azure OpenAI Vision** with bounding box annotations.

```bash
curl -X POST http://localhost:8000/idp/analyze \
  -H "X-API-Key: blackpool-architect-key-2024" \
  -F "image=@passport.jpg"
```

**Response:**
```json
{
  "document_type": "Passport",
  "confidence": "high",
  "extracted_fields": {
    "surname": "RODRIGUEZ",
    "given_names": "CLAUDIA MARCELA",
    "passport_number": "CB007001"
  },
  "annotations": {
    "surname": { "value": "RODRIGUEZ", "bbox": [0.1, 0.38, 0.6, 0.45] }
  }
}
```

---

### `GET /logs` — Request Logs
Returns all tracked requests from PostgreSQL (timestamp, endpoint, input, output, latency, external usage, HTTP status).

```bash
curl http://localhost:8000/logs \
  -H "X-API-Key: blackpool-architect-key-2024"
```

---

### `GET /health` — Health Check
```bash
curl http://localhost:8000/health
# {"status":"ok","version":"1.0.0"}
```

---

## Useful Commands

```bash
# Stop all services
docker compose down

# Stop and delete the database volume (full reset)
docker compose down -v

# View live logs from all containers
docker compose logs -f

# View API logs only
docker compose logs -f api

# Rebuild after code changes
docker compose up --build
```

---

## Project Structure

```
ai-technical-assessment/        ← repository root — run all commands here
├── api/
│   ├── app/
│   │   ├── core/               # Config, auth, database connection
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── routers/            # Endpoint handlers (stt, tts, idp, logs)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # External service integrations
│   │   ├── static/
│   │   │   └── index.html      # Full interactive SPA (no framework)
│   │   └── main.py             # FastAPI app entry point + static UI mount
│   ├── Dockerfile
│   └── requirements.txt
├── infra/
│   └── init.sql                # PostgreSQL schema (used by docker-compose.yml)
├── .github/workflows/          # CI/CD pipeline
├── docker-compose.yml          # ← THE compose file — run from repo root
├── .env.example                # Credential template — copy to .env and fill in
├── .gitignore
├── README.md
├── start.bat                   # Windows double-click launcher
├── stop.bat                    # Windows stop script
└── start.sh                    # Mac/Linux launcher
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `docker: command not found` | Install Docker Desktop and make sure it's running |
| `docker compose` can't find `docker-compose.yml` | Make sure you are in the `ai-technical-assessment/` root folder, **not** inside `api/` or `infra/` |
| Docker Desktop won't start on Windows | Run `wsl --install` in PowerShell as Administrator, then restart |
| Port 8000 already in use | Run `docker compose down` then try again |
| Port 5432 already in use | Stop any local PostgreSQL service |
| API returns 401 | Check your `X-API-Key` header matches the `API_KEY` value in your `.env` |
| STT/TTS/IDP return errors | Make sure you filled in valid API keys in `.env` |

---

## CI/CD

GitHub Actions pipeline (`.github/workflows/deploy.yml`) runs on every push to `main`:
1. Builds the Docker image
2. Pushes to GitHub Container Registry (`ghcr.io`)
3. Runs a smoke test (`GET /health`)
