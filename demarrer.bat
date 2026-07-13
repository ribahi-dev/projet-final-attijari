@echo off
REM ============================================================================
REM  NovaBank - Lancement en un double-clic (Windows)
REM
REM  Demarre TOUTE la plateforme (base de donnees + backend + frontend) avec
REM  Docker. Seul prerequis : Docker Desktop installe.
REM
REM  Utilisation : double-cliquer sur ce fichier.
REM ============================================================================
cd /d "%~dp0"
title NovaBank - Demarrage
chcp 65001 >nul 2>&1

echo.
echo   ========================================
echo      NovaBank - Plateforme bancaire IA
echo   ========================================
echo.

REM --- 1. Docker est-il installe ? ---
where docker >nul 2>nul
if %errorlevel% neq 0 goto no_docker

REM --- 2. Docker Desktop est-il demarre ? ---
docker info >nul 2>nul
if %errorlevel% equ 0 goto start_stack

echo   [INFO] Docker Desktop n'est pas encore demarre.
echo   Tentative de lancement automatique de Docker Desktop...
if exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
echo   Patiente pendant le demarrage de Docker (jusqu'a ~2 minutes)...
echo.

set /a _tries=0
:wait_docker
set /a _tries+=1
timeout /t 5 /nobreak >nul
docker info >nul 2>nul
if %errorlevel% equ 0 goto start_stack
if %_tries% geq 24 goto docker_timeout
goto wait_docker

:start_stack
echo.
echo   Preparation (reseau propre, liberation des ports)...
REM Repartir d'un reseau Docker propre pour CE projet : repare l'etat laisse
REM par un lancement precedent interrompu (sinon l'API ne joint plus "postgres").
docker compose down --remove-orphans >nul 2>&1
REM Si une AUTRE copie de NovaBank (lancee depuis un autre dossier) occupe
REM encore les ports 5433/8000/8090, l'arreter -> evite "port already allocated".
for /f %%c in ('docker ps -q --filter "publish=8090" --filter "publish=8000" --filter "publish=5433" 2^>nul') do docker stop %%c >nul 2>&1

echo.
echo   Demarrage des services...
echo   1ere fois : construction (connexion internet requise, 2 a 5 min).
echo   Ensuite   : demarrage instantane, meme SANS internet.
echo.
REM On n'utilise PAS --build : Docker construit les images si elles manquent,
REM puis les REUTILISE (aucun acces reseau). C'est ce qui rend la demo fiable
REM meme avec une connexion lente. Pour reconstruire apres une modif du code,
REM utiliser "reconstruire.bat".
docker compose up -d
if %errorlevel% equ 0 goto services_ok

echo.
echo   [INFO] Echec (souvent un telechargement d'image de base interrompu).
echo   Nouvelle tentative dans 8 secondes...
timeout /t 8 /nobreak >nul
docker compose up -d
if %errorlevel% neq 0 goto compose_failed

:services_ok
echo.
echo   Initialisation de la base de donnees et des donnees de demo...
timeout /t 12 /nobreak >nul

echo.
echo   ========================================
echo      NovaBank est prete !
echo   ========================================
echo.
echo   Application  :  http://localhost:8090
echo   API (Swagger):  http://localhost:8000/docs
echo.
echo   Comptes de demonstration :
echo     Directeur   : directeur@novabank.ma  / Directeur@2026!
echo     Conseiller  : conseiller@novabank.ma / Conseiller@2026!
echo     Admin       : admin@novabank.ma      / Admin@2026!
echo.
echo   Pour arreter la plateforme : double-clic sur "arreter.bat"
echo.
start "" http://localhost:8090
pause
exit /b 0

:no_docker
echo   [ERREUR] Docker n'est pas installe sur ce PC.
echo.
echo   Installe Docker Desktop, demarre-le, puis relance ce script :
echo   https://www.docker.com/products/docker-desktop/
echo.
pause
exit /b 1

:docker_timeout
echo.
echo   [ERREUR] Docker Desktop n'a pas fini de demarrer a temps.
echo   Ouvre Docker Desktop manuellement, attends que l'icone de la baleine
echo   soit stable, puis relance ce script.
echo.
pause
exit /b 1

:compose_failed
echo.
echo   [ERREUR] Le demarrage des services a echoue.
echo.
echo   Cause la plus frequente : la 1ere construction n'a pas pu TELECHARGER
echo   les images de base (node, nginx) depuis Docker Hub -- un probleme de
echo   CONNEXION, pas du projet.
echo.
echo   Que faire :
echo     1) Verifie ta connexion internet (le 1er lancement en a besoin).
echo     2) Relance ce script : le telechargement reprend ou il s'est arrete.
echo     3) Une fois construites, les images restent en cache : les lancements
echo        suivants marchent en quelques secondes, meme hors-ligne.
echo.
pause
exit /b 1
