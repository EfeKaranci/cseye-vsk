@echo off
REM Double-click to start the CSEYE bridge, then open http://127.0.0.1:8765/
title CSEYE bridge
"C:\Analysis\WC2026\.venv\Scripts\python.exe" "%~dp0run.py"
echo.
echo Bridge stopped. Close this window or press a key.
pause >nul
