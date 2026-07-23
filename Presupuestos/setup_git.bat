@echo off
REM ── Setup inicial del repositorio Git ──────────────────────────────────────
REM Ejecutar UNA SOLA VEZ desde la carpeta Costos_de_construccion
REM Reemplazá la URL con la de tu repo en GitHub antes de correr esto.

set REPO_URL=https://github.com/PanchoM2025/costos_de_construccion.git

cd /d "%~dp0"
git init
git remote add origin %REPO_URL%
git add -A
git commit -m "Primer commit - setup inicial"
git branch -M main
git push -u origin main

echo.
echo Listo! El repo quedó conectado a GitHub.
pause
