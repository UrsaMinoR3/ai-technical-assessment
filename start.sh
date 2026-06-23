#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  Blackpool Assessment — AI API Launcher (Mac / Linux)
#  Run with:  chmod +x start.sh && ./start.sh
#
#  Compose file : infra/docker-compose.yml
#  Credentials  : infra/.env
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; WHITE='\033[1;37m'; DIM='\033[2m'; NC='\033[0m'

# Compose command — always points to infra/
DC="docker compose -f infra/docker-compose.yml --env-file infra/.env"

echo ""
echo -e "${CYAN}  ╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}  ║                                                  ║${NC}"
echo -e "${CYAN}  ║   Blackpool Assessment — AI API Launcher         ║${NC}"
echo -e "${CYAN}  ║   FastAPI  ·  Deepgram  ·  Azure OpenAI          ║${NC}"
echo -e "${CYAN}  ║                                                  ║${NC}"
echo -e "${CYAN}  ╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ─── FAST PATH: Already running? ──────────────────────────────────────────────
if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓  API is already running!${NC}"
    echo ""
    echo -e "${CYAN}  ══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}  The application is LIVE at:${NC}"
    echo ""
    echo -e "${WHITE}    Web UI (main)  →  http://localhost:8000${NC}"
    echo -e "${WHITE}    Swagger docs   →  http://localhost:8000/docs${NC}"
    echo -e "${WHITE}    API Key        →  blackpool-architect-key-2024${NC}"
    echo ""
    echo -e "${DIM}    To stop:  $DC down${NC}"
    echo ""
    echo -e "${CYAN}  ══════════════════════════════════════════════════${NC}"
    echo ""
    if command -v open &>/dev/null; then
        open http://localhost:8000
    elif command -v xdg-open &>/dev/null; then
        xdg-open http://localhost:8000
    fi
    exit 0
fi

# ─── STEP 1: Check Docker ─────────────────────────────────────────────────────
echo -e "${WHITE}  [1/4] Checking Docker Desktop...${NC}"

if ! command -v docker &>/dev/null; then
    echo -e "${RED}  ✗  Docker is not installed.${NC}"
    echo -e "${YELLOW}  Download Docker Desktop: https://www.docker.com/products/docker-desktop/${NC}"
    exit 1
fi

if ! docker info &>/dev/null; then
    echo -e "${RED}  ✗  Docker is installed but not running.${NC}"
    echo -e "${WHITE}    Open Docker Desktop and wait for it to say 'Docker Desktop is running'${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓  $(docker --version)${NC}"
echo -e "${GREEN}  ✓  Docker daemon is running${NC}"
echo ""

# ─── STEP 2: Check infra/.env ─────────────────────────────────────────────────
echo -e "${WHITE}  [2/4] Checking credentials (infra/.env)...${NC}"

if [ ! -f "infra/.env" ]; then
    echo -e "${YELLOW}  !  infra/.env not found.${NC}"
    echo ""
    if [ ! -f "infra/.env.example" ]; then
        echo -e "${RED}  ✗  infra/.env.example also missing — re-clone the repository.${NC}"
        exit 1
    fi
    cp infra/.env.example infra/.env
    echo -e "${YELLOW}  →  Created infra/.env from template — fill in your API keys.${NC}"
    echo ""
    echo -e "${WHITE}  Required keys in infra/.env:${NC}"
    echo -e "${DIM}    AZURE_OPENAI_KEY      — your Azure OpenAI (or OpenAI) API key${NC}"
    echo -e "${DIM}    AZURE_OPENAI_BASE_URL — e.g. https://api.openai.com/v1/${NC}"
    echo -e "${DIM}    AZURE_OPENAI_MODEL    — e.g. gpt-4o${NC}"
    echo -e "${DIM}    DEEPGRAM_API_KEY      — your Deepgram API key${NC}"
    echo -e "${DIM}    API_KEY               — any string as the local API password${NC}"
    echo ""
    read -r -p "  Open infra/.env in your editor, fill in values, then press ENTER..."
    echo ""
else
    echo -e "${GREEN}  ✓  infra/.env found${NC}"
fi
echo ""

# ─── STEP 3: Build and start ──────────────────────────────────────────────────
echo -e "${WHITE}  [3/4] Building and starting containers...${NC}"
echo -e "${DIM}       (First run: 2-5 min for Docker image downloads)${NC}"
echo -e "${DIM}       (After first run: under 30 seconds)${NC}"
echo ""

if ! $DC up --build -d; then
    echo ""
    echo -e "${RED}  ✗  docker compose failed.${NC}"
    echo -e "${YELLOW}  Common fixes:${NC}"
    echo -e "${WHITE}    Port 8000 in use?  →  $DC down && try again${NC}"
    echo -e "${WHITE}    Port 5432 in use?  →  stop local PostgreSQL first${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}  ✓  Containers started${NC}"
echo ""

# ─── STEP 4: Health check ─────────────────────────────────────────────────────
echo -e "${WHITE}  [4/4] Waiting for API to be ready...${NC}"

ATTEMPTS=0
until curl -sf http://localhost:8000/health >/dev/null 2>&1; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ "$ATTEMPTS" -gt 45 ]; then
        echo ""
        echo -e "${RED}  ✗  API did not start after 90 seconds.${NC}"
        echo -e "${YELLOW}  Check logs: $DC logs api${NC}"
        exit 1
    fi
    sleep 2
done

echo ""
echo -e "${GREEN}  ✓  API is live and healthy!${NC}"
echo ""

# ─── Done ─────────────────────────────────────────────────────────────────────
echo -e "${CYAN}  ══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}  The application is LIVE at:${NC}"
echo ""
echo -e "${WHITE}    Web UI (main)  →  http://localhost:8000${NC}"
echo -e "${WHITE}    Swagger docs   →  http://localhost:8000/docs${NC}"
echo -e "${WHITE}    API Key        →  blackpool-architect-key-2024${NC}"
echo ""
echo -e "${DIM}    To stop:  $DC down${NC}"
echo -e "${CYAN}  ══════════════════════════════════════════════════${NC}"
echo ""

sleep 2
if command -v open &>/dev/null; then
    open http://localhost:8000
elif command -v xdg-open &>/dev/null; then
    xdg-open http://localhost:8000
fi
