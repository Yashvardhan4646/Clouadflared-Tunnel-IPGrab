@echo off
cd /d "%~dp0"

start "" python server.py
timeout /t 2 /nobreak >nul
cloudflared tunnel --url http://localhost:6767

pause