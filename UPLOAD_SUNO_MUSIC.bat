@echo off
chcp 65001 >nul
title Suno AI Music Uploader to Catbox
echo ===================================================
echo   Uploading Suno AI Music to Catbox & GitHub Sync
echo ===================================================
python "%~dp0upload_suno_music_to_catbox.py"
echo.
echo Process complete.
pause
