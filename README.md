# AI Technical Assessment API

REST API built with **FastAPI** integrating **Azure OpenAI** (document analysis) and **Deepgram** (speech-to-text / text-to-speech), backed by **PostgreSQL** for request tracking.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/UrsaMinoR3/ai-technical-assessment.git
cd ai-technical-assessment

# 2. Set up credentials
cp infra/.env.example infra/.env
# Edit infra/.env and fill in real values

# 3. Launch everything
cd infra && docker compose up --build
```

The API will be available at `http://localhost:8000`
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## Endpoints

All endpoints require the `X-API-Key` header.

### `POST /stt` — Speech-to-Text
Transcribes an MP3 or WAV audio file using Deepgram Nova-2.

```bash
curl -X POST http://localhost:8000/stt \
  -H "X-API-Key: your_api_key" \
  -F "audio=@your_file.mp3"
```

**Response:**
```json
{
  "transcript": "Hello world",
  "language": "en",
  "duration": 3.5,
  "speakers": [
    { "speaker": 0, "start": 0.0, "end": 1.5, "text": "Hello" },
    { "speaker": 1, "start": 1.6, "end": 3.5, "text": "world" }
  ]
}
```

### `POST /tts` — Text-to-Speech
Synthesizes text to downloadable MP3 using Deepgram Aura.

```bash
curl -X POST http://localhost:8000/tts \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice": "aura-asteria-en"}' \
  --output speech.mp3
```

### `POST /idp/analyze` — Intelligent Document Processing
Extracts structured data from a document image using Azure OpenAI.

```bash
curl -X POST http://localhost:8000/idp/analyze \
  -H "X-API-Key: your_api_key" \
  -F "image=@document.jpg"
```

**Response:**
```json
{
  "document_type": "national_id",
  "extracted_fields": {
    "full_name": "John Doe",
    "id_number": "123456789",
    "date_of_birth": "1990-01-01"
  },
  "confidence": "high"
}
```

---

## Project Structure

```
ai-technical-assessment/
├── api/
│   ├── app/
│   │   ├── core/        # Config, auth, database
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routers/     # Endpoint handlers
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # External service integrations
│   │   └── main.py      # FastAPI app entry point
│   ├── Dockerfile
│   └── requirements.txt
├── infra/
│   ├── docker-compose.yml
│   ├── init.sql
│   └── .env.example
├── docs/
└── tests/
```

---

## Environment Variables

Copy `infra/.env.example` to `infra/.env` and fill in the values:

| Variable | Description |
|----------|-------------|
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_NAME` | Database name |
| `API_KEY` | Your internal API key (X-API-Key header) |
| `AZURE_OPENAI_KEY` | Azure OpenAI API key |
| `AZURE_OPENAI_BASE_URL` | Azure OpenAI base URL |
| `AZURE_OPENAI_MODEL` | Deployment model name |
| `DEEPGRAM_API_KEY` | Deepgram API key |

> **Security note:** Never commit `.env` files. Real credentials are managed via `.gitignore` locally and GitHub Secrets for CI/CD.
