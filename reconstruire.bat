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

echo   Reconstruction COMPLETE (--no-cache, connexion internet requise)...
echo   A n'utiliser que si "demarrer.bat" affiche un comportement anormal.
echo.
REM Reseau propre + liberation des ports (cf. demarrer.bat) avant de rebatir.
docker compose down --remove-orphans >nul 2>&1
for /f %%c in ('docker ps -q --filter "publish=8090" --filter "publish=8000" --filter "publish=5433" 2^>nul') do docker stop %%c >nul 2>&1
REM --no-cache : on reconstruit TOUT de zero (re-telecharge les dependances)
REM -> garantit une image parfaitement a jour, meme si le cache etait corrompu.
docker compose build --no-cache
if %errorlevel% neq 0 goto retry
docker compose up -d
if %errorlevel% equ 0 goto ok

:retry
echo.
echo   [INFO] Echec (telechargement interrompu ?). Nouvelle tentative...
timeout /t 8 /nobreak >nul
docker compose build --no-cache && docker compose up -d
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
