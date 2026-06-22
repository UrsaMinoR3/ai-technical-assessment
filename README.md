# Blackpool Assessment — AI REST API

REST API built with **FastAPI** integrating **Azure OpenAI** (document analysis) and **Deepgram** (speech-to-text / text-to-speech), backed by **PostgreSQL** for request tracking.

The project ships with a full **interactive web UI** — no Swagger needed. Open `http://localhost:8000` after launching.

---

## Prerequisites

| Requirement | Version | Notes |
|------------|---------|-------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 4.0+ | **Required** — handles Python, PostgreSQL, everything |
| Git | any | To clone the repo |

> Docker Desktop must be **running** before you launch the project. Everything else (Python, dependencies, database) is handled automatically inside containers.

---

## Quick Start

### Option A — Double-click launcher (Windows)

1. Clone the repo
2. Copy `.env.example` → `.env` and fill in your API keys  
3. Double-click **`start.bat`**

The script checks Docker, sets up the environment, builds the containers, waits for the API to be healthy, and opens your browser automatically.

---

### Option B — Manual (any OS)

```bash
# 1. Clone
git clone https://github.com/UrsaMinoR3/ai-technical-assessment.git
cd ai-technical-assessment

# 2. Set up credentials
cp .env.example .env
# Open .env and fill in your real API keys (see table below)

# 3. Launch
docker compose up --build
```

**Mac / Linux users:** use the shell script instead:
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
| `API_KEY` | Your internal API key sent in `X-API-Key` header |
| `AZURE_OPENAI_KEY` | Azure OpenAI (or OpenAI) API key |
| `AZURE_OPENAI_BASE_URL` | API base URL (e.g. `https://api.openai.com/v1/`) |
| `AZURE_OPENAI_MODEL` | Model name (e.g. `gpt-4o`) |
| `DEEPGRAM_API_KEY` | Deepgram API key |

> **Security:** `.env` is in `.gitignore` — real credentials are never committed. CI/CD uses GitHub Secrets.

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
Extracts structured fields from a document image using **Azure OpenAI GPT-4o Vision** with bounding box annotations.

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

# View live logs
docker compose logs -f

# View API logs only
docker compose logs -f api
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
│   │   └── main.py         # FastAPI app entry point + static UI mount
│   ├── static/
│   │   └── index.html      # Full interactive SPA (no framework)
│   ├── Dockerfile
│   └── requirements.txt
├── infra/
│   ├── docker-compose.yml  # Original infra compose
│   ├── init.sql            # PostgreSQL schema
│   └── .env.example
├── docker-compose.yml      # Root compose (use this one)
├── .env.example            # Credential template
├── start.bat               # Windows launcher (double-click)
└── start.sh                # Mac/Linux launcher
```

---

## CI/CD

GitHub Actions pipeline (`.github/workflows/`) runs on every push to `main`:
1. Builds the Docker image
2. Pushes to GitHub Container Registry (`ghcr.io`)
3. Runs a smoke test (`GET /health`)
