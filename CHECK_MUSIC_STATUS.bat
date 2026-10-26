@echo off
chcp 65001 >nul
title KRISHNA VIBEZ - MUSIC QUEUE STATUS
cls
echo =================================================================
echo        KRISHNA VIBEZ -- MASTER AI MUSIC INVENTORY STATUS
echo =================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "& {
    $base = 'E:\Paresh\Auto Post\Auto-Insta-Krishna'
    
    function Get-Count($file) {
        $p = Join-Path $base $file
        if (Test-Path $p) {
            $lines = Get-Content $p | Where-Object { $_.Trim() -ne '' -and -not $_.Trim().StartsWith('#') }
            return $lines.Count
        }
        return 0
    }
    
    $suno_active = Get-Count 'suno_music_urls.txt'
    $suno_backup = Get-Count 'suno_music_urls_backup.txt'
    $suno_used   = Get-Count 'suno_music_used_urls.txt'
    
    $treblo_active = Get-Count 'treblo_music_urls.txt'
    $treblo_backup = Get-Count 'treblo_music_urls_backup.txt'
    $treblo_used   = Get-Count 'treblo_music_used_urls.txt'
    
    $total_active = $suno_active + $treblo_active
    $total_backup = $suno_backup + $treblo_backup
    
    Write-Host '  --- [1] SUNO AI MUSIC STATUS ---' -ForegroundColor Cyan
    Write-Host ('    Active Queue (Ready to use) : ' + $suno_active + ' tracks') -ForegroundColor Yellow
    Write-Host ('    Master Backup Pool          : ' + $suno_backup + ' tracks')
    Write-Host ('    Already Used / Uploaded     : ' + $suno_used + ' tracks')
    Write-Host ''
    
    Write-Host '  --- [2] TREBLO AI MUSIC STATUS ---' -ForegroundColor Green
    Write-Host ('    Active Queue (Fallback)     : ' + $treblo_active + ' tracks') -ForegroundColor Yellow
    Write-Host ('    Master Backup Pool          : ' + $treblo_backup + ' tracks')
    Write-Host ('    Already Used / Uploaded     : ' + $treblo_used + ' tracks')
    Write-Host ''
    
    Write-Host '  ==================================================' -ForegroundColor DarkGray
    Write-Host ('    TOTAL ACTIVE QUEUE (Combined) : ' + $total_active + ' tracks') -ForegroundColor White
    Write-Host ('    TOTAL MASTER BACKUP POOL      : ' + $total_backup + ' tracks') -ForegroundColor White
    Write-Host '  ==================================================' -ForegroundColor DarkGray
}"

echo.
echo =================================================================
pause
