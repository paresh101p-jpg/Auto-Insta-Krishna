@echo off
title Treblo OGG to WAV Converter
color 0b
echo ========================================================
echo       TREBLO OGG TO WAV AUDIO CONVERTER (FFMPEG)
echo ========================================================
echo.

set "SOURCE_DIR=%USERPROFILE%\Downloads\Treblo_Music"

if not exist "%SOURCE_DIR%" (
    echo [!] Folder nahi mila: %SOURCE_DIR%
    echo Checking current folder instead...
    set "SOURCE_DIR=.\Treblo Music\uploaded"
)

echo Scanning for .ogg files in: %SOURCE_DIR%
echo.

setlocal enabledelayedexpansion
set COUNT=0

for %%F in ("%SOURCE_DIR%\*.ogg") do (
    set /a COUNT+=1
    echo [!COUNT!] Converting: %%~nxF -^> %%~nF.wav
    ffmpeg -y -i "%%F" -c:a pcm_s16le -ar 44100 "%SOURCE_DIR%\%%~nF.wav" -loglevel error
)

if %COUNT% EQU 0 (
    echo [INFO] Koi .ogg file nahi mili converting ke liye. Sabhi files pehle se WAV ho sakti hain!
) else (
    echo.
    echo ========================================================
    echo  SUCCESS: %COUNT% files converted to 100%% Studio WAV!
    echo ========================================================
)

echo.
pause
