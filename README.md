# Blackpool Assessment — AI REST API

REST API built with **FastAPI** integrating **Azure OpenAI** (document analysis) and **Deepgram** (speech-to-text / text-to-speech), backed by **PostgreSQL** for request tracking.

The project ships with a full **interactive web UI** — no Swagger needed. Open `http://localhost:8000` after launching.

---

## Prerequisites

### Windows — required one-time setup before installing Docker

Docker Desktop on Windows requires WSL 2 (Windows Subsystem for Linux). Run this **first**, in PowerShell as Administrator:

```powershell
wsl --install
```

Restart your computer when prompted, then install Docker Desktop.

---

### All platforms

| Requirement | Version | Notes |
|------------|---------|-------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 4.0+ | **Required** — handles Python, PostgreSQL, everything |
| Git | any | To clone the repo |

> Docker Desktop must be **running** before you launch the project. Everything else (Python, dependencies, database) is handled automatically inside containers.

---

## Quick Start

### Option A — Double-click launcher (Windows)

1. Clone the repo
2. Fill in your API keys in **`infra/.env`**
3. Double-click **`start.bat`**

The script checks Docker, verifies credentials, builds the containers, waits for the API to be healthy, and opens your browser automatically.

---

### Option B — Manual (any OS)

```bash
# 1. Clone and enter the repo
git clone https://github.com/UrsaMinoR3/ai-technical-assessment.git
cd ai-technical-assessment

# 2. Set up credentials
cp infra/.env.example infra/.env
# Open infra/.env and fill in your real API keys

# 3. Launch
docker compose -f infra/docker-compose.yml --env-file infra/.env up --build
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

**API Key:** set in `infra/.env` under `API_KEY`

---

## Environment Variables

All credentials live in **`infra/.env`** (gitignored — never committed).  
Copy `infra/.env.example` → `infra/.env` and fill in the values:

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

> **Security:** `infra/.env` is listed in `.gitignore` — real credentials are never committed. CI/CD uses GitHub Secrets.

---

## Endpoints

All endpoints except `/health` require the `X-API-Key` header.

### `POST /stt` — Speech-to-Text
Transcribes an MP3 or WAV file using **Deepgram Nova-2** with speaker diarization and auto language detection.

```bash
curl -X POST http://localhost:8000/stt \
  -H "X-API-Key: your-api-key" \
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
  -H "X-API-Key: your-api-key" \
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
  -H "X-API-Key: your-api-key" \
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
  -H "X-API-Key: your-api-key"
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
docker compose -f infra/docker-compose.yml --env-file infra/.env down

# Stop and delete the database volume (full reset)
docker compose -f infra/docker-compose.yml --env-file infra/.env down -v

# View live logs from all containers
docker compose -f infra/docker-compose.yml --env-file infra/.env logs -f

# View API logs only
docker compose -f infra/docker-compose.yml --env-file infra/.env logs -f api

# Rebuild after code changes
docker compose -f infra/docker-compose.yml --env-file infra/.env up --build
```

---

## Project Structure

```
ai-technical-assessment/
├── api/
│   ├── app/
│   │   ├── core/           # Config, auth, database connection
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── routers/        # Endpoint handlers (stt, tts, idp, logs)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # External service integrations
│   │   ├── static/
│   │   │   └── index.html  # Full interactive SPA (no framework)
│   │   └── main.py         # FastAPI app entry point + static UI mount
│   ├── Dockerfile
│   └── requirements.txt
├── infra/
│   ├── docker-compose.yml  # ← THE compose file
│   ├── init.sql            # PostgreSQL schema
│   └── .env.example        # Credential template — copy to infra/.env
├── docs/
├── tests/
├── .github/workflows/      # CI/CD pipeline
├── .gitignore
├── README.md
├── start.bat               # Windows double-click launcher
├── stop.bat                # Windows stop script
└── start.sh                # Mac/Linux launcher
```

---

## CI/CD

GitHub Actions pipeline (`.github/workflows/`) runs on every push to `main`:
1. Builds the Docker image
2. Pushes to GitHub Container Registry (`ghcr.io`)
3. Runs a smoke test (`GET /health`)
