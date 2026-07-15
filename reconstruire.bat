@echo off
REM ============================================================================
REM  NovaBank - Reconstruire + REINITIALISER (Windows)
REM
REM  A utiliser apres avoir MIS A JOUR LE CODE (nouveau ZIP / git pull) :
REM   - reconstruit les images depuis le code present ;
REM   - REINITIALISE la base de donnees (indispensable si le schema a change,
REM     ex. nouvelles colonnes) puis re-injecte les donnees de demonstration.
REM
REM  ⚠️ La base est remise a zero (les donnees de demo sont recreees). C'est
REM  sans risque : ce sont des donnees simulees.
REM
REM  Pour un simple demarrage sans reset, utiliser "demarrer.bat".
REM ============================================================================
cd /d "%~dp0"
title NovaBank - Reconstruction
chcp 65001 >nul 2>&1

echo.
echo   ========================================
echo      NovaBank - Reconstruction + reset base
echo   ========================================
echo.

docker info >nul 2>nul
if %errorlevel% neq 0 (
  echo   [ERREUR] Docker Desktop n'est pas demarre. Lance-le puis reessaie.
  pause
  exit /b 1
)

echo   Reinitialisation de la base + reconstruction depuis le code...
echo   (les donnees de demo seront recreees automatiquement)
echo.
REM down -v : supprime AUSSI le volume de la base -> au redemarrage, les tables
REM sont recreees avec le schema A JOUR (corrige "colonne manquante" apres une
REM mise a jour du code). --remove-orphans nettoie le reseau.
docker compose down -v --remove-orphans >nul 2>&1
REM Liberer les ports si une autre copie occupe encore 5433/8000/8090.
for /f %%c in ('docker ps -q --filter "publish=8090" --filter "publish=8000" --filter "publish=5433" 2^>nul') do docker stop %%c >nul 2>&1

REM up -d --build : reconstruit les images depuis le code (cache -> rapide et
REM hors-ligne une fois les images de base telechargees).
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
echo   Base reinitialisee et services redemarres.
echo   Application : http://localhost:8090
echo.
start "" http://localhost:8090
pause
exit /b 0
