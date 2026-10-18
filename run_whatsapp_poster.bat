@echo off
title WhatsApp Channel Auto-Poster (Krishna Vibez)
cd /d "%~dp0"

echo =========================================================
echo   WhatsApp Channel Auto-Poster (Krishna Vibez)
echo =========================================================
echo.

set PYTHON_EXE=C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe
set PYTHONIOENCODING=utf-8
chcp 65001 >nul

if not exist "%PYTHON_EXE%" (
    echo Error: Python not found at %PYTHON_EXE%
    pause
    exit /b 1
)

"%PYTHON_EXE%" -u whatsapp_channel_poster.py

echo.
echo =========================================================
echo   Job Completed.
echo =========================================================
pause
