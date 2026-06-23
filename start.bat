@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

:: ─────────────────────────────────────────────────────────────────────────────
::  Blackpool Assessment — AI API Launcher
::  Double-click this file on Windows to start everything automatically.
::
::  Compose file : infra/docker-compose.yml
::  Credentials  : infra/.env
:: ─────────────────────────────────────────────────────────────────────────────

:: Enable ANSI colors (Windows 10/11)
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

set "C_CYAN=[36m"
set "C_GREEN=[32m"
set "C_YELLOW=[33m"
set "C_RED=[31m"
set "C_WHITE=[97m"
set "C_DIM=[90m"
set "C_RESET=[0m"

:: Compose command — always points to infra/
set "DC=docker compose -f infra\docker-compose.yml --env-file infra\.env"

cls
echo.
echo %C_CYAN%  ╔══════════════════════════════════════════════════╗%C_RESET%
echo %C_CYAN%  ║                                                  ║%C_RESET%
echo %C_CYAN%  ║   Blackpool Assessment — AI API Launcher         ║%C_RESET%
echo %C_CYAN%  ║   FastAPI  ·  Deepgram  ·  Azure OpenAI          ║%C_RESET%
echo %C_CYAN%  ║                                                  ║%C_RESET%
echo %C_CYAN%  ╚══════════════════════════════════════════════════╝%C_RESET%
echo.

:: ─── FAST PATH: Already running? ──────────────────────────────────────────────
curl -s -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %C_GREEN%  ✓  API is already running!%C_RESET%
    echo.
    echo %C_CYAN%  ══════════════════════════════════════════════════%C_RESET%
    echo.
    echo %C_GREEN%  The application is LIVE at:%C_RESET%
    echo.
    echo %C_WHITE%    Web UI (main)  →  http://localhost:8000%C_RESET%
    echo %C_WHITE%    Swagger docs   →  http://localhost:8000/docs%C_RESET%
    echo %C_WHITE%    API Key        →  blackpool-architect-key-2024%C_RESET%
    echo.
    echo %C_DIM%    To stop:  double-click stop.bat%C_RESET%
    echo.
    echo %C_CYAN%  ══════════════════════════════════════════════════%C_RESET%
    echo.
    echo %C_WHITE%  Opening browser...%C_RESET%
    start http://localhost:8000
    echo.
    echo %C_DIM%  This window will close automatically in 10 seconds...%C_RESET%
    timeout /t 10 /nobreak
    goto :EOF
)

:: ─── STEP 1: Check Docker ─────────────────────────────────────────────────────
echo %C_WHITE%  [1/4] Checking Docker Desktop...%C_RESET%
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo %C_RED%  ✗  Docker is not installed or not in PATH.%C_RESET%
    echo.
    echo %C_YELLOW%  To fix this:%C_RESET%
    echo %C_WHITE%    1. Download Docker Desktop: https://www.docker.com/products/docker-desktop/%C_RESET%
    echo %C_WHITE%    2. Install it and restart your computer%C_RESET%
    echo %C_WHITE%    3. Run this launcher again%C_RESET%
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('docker --version 2^>nul') do set DOCKER_VER=%%v
echo %C_GREEN%  ✓  !DOCKER_VER!%C_RESET%

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo %C_RED%  ✗  Docker Desktop is installed but not running.%C_RESET%
    echo.
    echo %C_YELLOW%  To fix this:%C_RESET%
    echo %C_WHITE%    1. Open Docker Desktop from your Start menu or taskbar%C_RESET%
    echo %C_WHITE%    2. Wait until the whale icon says "Docker Desktop is running"%C_RESET%
    echo %C_WHITE%    3. Run this launcher again%C_RESET%
    echo.
    pause
    exit /b 1
)
echo %C_GREEN%  ✓  Docker daemon is running%C_RESET%
echo.

:: ─── STEP 2: Check infra\.env ─────────────────────────────────────────────────
echo %C_WHITE%  [2/4] Checking credentials (infra\.env)...%C_RESET%

if not exist "infra\.env" (
    echo %C_YELLOW%  !  infra\.env not found.%C_RESET%
    echo.
    if not exist "infra\.env.example" (
        echo %C_RED%  ✗  infra\.env.example also missing — re-clone the repository.%C_RESET%
        pause
        exit /b 1
    )
    copy "infra\.env.example" "infra\.env" >nul
    echo %C_YELLOW%  →  Created infra\.env from template — fill in your API keys.%C_RESET%
    echo.
    echo %C_WHITE%  Required keys in infra\.env:%C_RESET%
    echo %C_DIM%    AZURE_OPENAI_KEY      — your Azure OpenAI (or OpenAI) API key%C_RESET%
    echo %C_DIM%    AZURE_OPENAI_BASE_URL — e.g. https://api.openai.com/v1/%C_RESET%
    echo %C_DIM%    AZURE_OPENAI_MODEL    — e.g. gpt-4o%C_RESET%
    echo %C_DIM%    DEEPGRAM_API_KEY      — your Deepgram API key%C_RESET%
    echo %C_DIM%    API_KEY               — any string as the local API password%C_RESET%
    echo.
    set /p "OPEN_ENV=  Type 'open' to edit in Notepad now, or press ENTER to skip: "
    if /i "!OPEN_ENV!"=="open" (
        start notepad "infra\.env"
        echo.
        echo %C_YELLOW%  Edit and SAVE infra\.env in Notepad, then come back here.%C_RESET%
        pause
    )
) else (
    echo %C_GREEN%  ✓  infra\.env found%C_RESET%
)
echo.

:: ─── STEP 3: Build and start ──────────────────────────────────────────────────
echo %C_WHITE%  [3/4] Building and starting containers...%C_RESET%
echo %C_DIM%       (First run: 2-5 min for Docker image downloads)%C_RESET%
echo %C_DIM%       (After first run: under 30 seconds)%C_RESET%
echo.

%DC% up --build -d
if %errorlevel% neq 0 (
    echo.
    echo %C_RED%  ✗  docker compose failed. See error output above.%C_RESET%
    echo.
    echo %C_YELLOW%  Common fixes:%C_RESET%
    echo %C_WHITE%    • Port 8000 in use?  →  double-click stop.bat, then try again%C_RESET%
    echo %C_WHITE%    • Port 5432 in use?  →  stop any local PostgreSQL service%C_RESET%
    echo %C_WHITE%    • .env syntax error? →  check infra\.env has no extra spaces or quotes%C_RESET%
    echo.
    pause
    exit /b 1
)
echo.
echo %C_GREEN%  ✓  Containers started%C_RESET%
echo.

:: ─── STEP 4: Health check ─────────────────────────────────────────────────────
echo %C_WHITE%  [4/4] Waiting for API to be ready...%C_RESET%
set ATTEMPTS=0
:HEALTHCHECK
set /a ATTEMPTS+=1
if %ATTEMPTS% gtr 45 (
    echo.
    echo %C_RED%  ✗  API did not become healthy after 90 seconds.%C_RESET%
    echo.
    echo %C_YELLOW%  Diagnosis commands:%C_RESET%
    echo %C_WHITE%    %DC% logs api%C_RESET%
    echo %C_WHITE%    %DC% ps%C_RESET%
    echo.
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul 2>&1
curl -s -f http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    set /a DOTS=ATTEMPTS %% 4
    if !DOTS!==0 echo|set /p="."
    goto HEALTHCHECK
)

echo.
echo %C_GREEN%  ✓  API is live and healthy!%C_RESET%
echo.

:: ─── Done ─────────────────────────────────────────────────────────────────────
echo %C_CYAN%  ══════════════════════════════════════════════════%C_RESET%
echo.
echo %C_GREEN%  The application is LIVE at:%C_RESET%
echo.
echo %C_WHITE%    Web UI (main)  →  http://localhost:8000%C_RESET%
echo %C_WHITE%    Swagger docs   →  http://localhost:8000/docs%C_RESET%
echo %C_WHITE%    API Key        →  blackpool-architect-key-2024%C_RESET%
echo.
echo %C_DIM%    Services running in background — to stop: double-click stop.bat%C_RESET%
echo.
echo %C_CYAN%  ══════════════════════════════════════════════════%C_RESET%
echo.
echo %C_WHITE%  Opening browser...%C_RESET%
start http://localhost:8000
echo.
echo %C_DIM%  This window will close automatically in 10 seconds...%C_RESET%
timeout /t 10 /nobreak
endlocal
