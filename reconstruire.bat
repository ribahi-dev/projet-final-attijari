@echo off
REM ============================================================================
REM  NovaBank - Reconstruire les images (Windows)
REM
REM  A utiliser UNIQUEMENT apres avoir modifie le code : force la reconstruction
REM  des images Docker (necessite une connexion internet la 1ere fois pour
REM  telecharger les images de base). Pour un simple demarrage, utiliser
REM  "demarrer.bat" qui reutilise les images deja construites (hors-ligne).
REM ============================================================================
cd /d "%~dp0"
title NovaBank - Reconstruction
chcp 65001 >nul 2>&1

echo.
echo   ========================================
echo      NovaBank - Reconstruction des images
echo   ========================================
echo.

docker info >nul 2>nul
if %errorlevel% neq 0 (
  echo   [ERREUR] Docker Desktop n'est pas demarre. Lance-le puis reessaie.
  pause
  exit /b 1
)

echo   Reconstruction (connexion internet requise)...
echo.
REM Reseau propre + liberation des ports (cf. demarrer.bat) avant de rebatir.
docker compose down --remove-orphans >nul 2>&1
for /f %%c in ('docker ps -q --filter "publish=8090" --filter "publish=8000" --filter "publish=5433" 2^>nul') do docker stop %%c >nul 2>&1
docker compose up -d --build
if %errorlevel% equ 0 goto ok

echo.
echo   [INFO] Echec (telechargement d'image interrompu ?). Nouvelle tentative...
timeout /t 8 /nobreak >nul
docker compose up -d --build
if %errorlevel% neq 0 (
  echo.
  echo   [ERREUR] La reconstruction a echoue -- souvent un probleme de connexion
  echo   pour telecharger les images de base. Verifie internet et relance.
  echo.
  pause
  exit /b 1
)

:ok
echo.
echo   Images reconstruites et services redemarres.
echo   Application : http://localhost:8090
echo.
pause
exit /b 0
