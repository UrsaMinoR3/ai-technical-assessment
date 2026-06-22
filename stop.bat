@echo off
cd /d "%~dp0"
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

echo.
echo [36m  Blackpool Assessment — Stopping services...[0m
echo.

docker compose down
if %errorlevel% equ 0 (
    echo.
    echo [32m  ✓  All containers stopped.[0m
    echo [90m     Run start.bat to start again.[0m
) else (
    echo.
    echo [33m  Could not stop containers. Are they already stopped?[0m
    echo [90m     Check status: docker compose ps[0m
)
echo.
pause
