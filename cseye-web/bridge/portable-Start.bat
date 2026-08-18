@echo off
REM ===================================================================
REM  CSEYE - portable local viewer.  Double-click this file to start.
REM  No install and no admin rights needed. Requires ETABS on this PC.
REM ===================================================================
title CSEYE (local viewer)
cd /d "%~dp0"
echo.
echo   Starting CSEYE...
echo   A browser tab will open at  http://127.0.0.1:8766/
echo   Keep this window open. Close it (or press Ctrl+C) to stop CSEYE.
echo.
"%~dp0python\python.exe" "%~dp0app\bridge\launcher.py"
echo.
echo   CSEYE stopped. You can close this window.
pause >nul
