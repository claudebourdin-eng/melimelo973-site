@echo off
chcp 65001 >nul
echo.
echo  Lancement de l'installation Meli-Melo 973...
echo.

:: Vérifier les droits administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  Redemarrage en mode administrateur...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && LANCER_INSTALLATION.bat' -Verb RunAs"
    exit /b
)

:: Lancer le script PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALLER.ps1"
pause
