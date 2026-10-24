@echo off
title Auto-Insta-Krishna Master Automation
cd /d "%~dp0"

echo =========================================================
echo   Auto-Insta-Krishna: Resuming All Automation Workers
echo =========================================================
echo.

set PYTHON_EXE=C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe

echo [1/3] Starting Reel Generation Engine (batch_create_reels.py)...
start /b "" "%PYTHON_EXE%" batch_create_reels.py

echo [2/3] Starting Images Catbox Uploader (catbox_uploader.py)...
start /b "" "%PYTHON_EXE%" catbox_uploader.py

echo [3/3] Starting Pipeline Watcher & Reel Uploader (watch_and_upload_reels.py)...
start /b "" "%PYTHON_EXE%" watch_and_upload_reels.py

echo [4/4] Starting Suno Music & Live Auto-Watcher (watch_and_upload_suno_music.py)...
start /b "" "%PYTHON_EXE%" watch_and_upload_suno_music.py

echo.
echo =========================================================
echo   All 4 workers are running in the background!
echo   Work will resume right from where it left off.
echo =========================================================
pause
