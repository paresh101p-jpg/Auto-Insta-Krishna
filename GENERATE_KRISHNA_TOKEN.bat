@echo off
title Krishna YouTube OAuth Token Generator
color 0a
echo =================================================================
echo   KRISHNA YOUTUBE OAUTH TOKEN GENERATOR
echo =================================================================
echo.
set "PY=python"
if exist "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe" set "PY=C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
if exist "C:\Users\Admin\AppData\Local\Programs\Python\Python310\python.exe" set "PY=C:\Users\Admin\AppData\Local\Programs\Python\Python310\python.exe"
if exist "C:\Program Files\Python311\python.exe" set "PY=C:\Program Files\Python311\python.exe"

echo Browser me Google Sign-in page open ho raha hai...
echo.
"%PY%" "%~dp0get_youtube_token.py"
echo.
echo =================================================================
pause
