@echo off
winget install cloudflared
pause
(goto) 2>nul & del "%~f0"