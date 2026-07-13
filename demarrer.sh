#!/usr/bin/env bash
# =============================================================================
#  NovaBank - Lancement en une commande (macOS / Linux)
#
#  Demarre TOUTE la plateforme (base + backend + frontend) avec Docker.
#  Prerequis unique : Docker installe et demarre.
#
#  Utilisation :  ./demarrer.sh    (ou double-clic selon le systeme)
# =============================================================================
set -e
cd "$(dirname "$0")"

echo ""
echo "  ========================================"
echo "     NovaBank - Plateforme bancaire IA"
echo "  ========================================"
echo ""

# 1. Docker installe ?
if ! command -v docker >/dev/null 2>&1; then
  echo "  [ERREUR] Docker n'est pas installe."
  echo "  Installe Docker Desktop : https://www.docker.com/products/docker-desktop/"
  exit 1
fi

# 2. Docker demarre ?
if ! docker info >/dev/null 2>&1; then
  echo "  [ERREUR] Docker n'est pas demarre. Lance Docker Desktop puis reessaie."
  exit 1
fi

# On n'utilise PAS --build : Docker construit les images si elles manquent
# (1ere fois, internet requis) puis les REUTILISE (aucun acces reseau) ->
# demarrage fiable meme hors-ligne. Pour reconstruire apres une modif du
# code, utiliser "./reconstruire.sh".
echo "  Demarrage des services..."
echo "  1ere fois : construction (internet requis, 2 a 5 min)."
echo "  Ensuite   : demarrage instantane, meme sans internet."
echo ""
if ! docker compose up -d; then
  echo ""
  echo "  [INFO] Echec (telechargement d'image interrompu ?). Nouvelle tentative..."
  sleep 8
  docker compose up -d
fi

echo ""
echo "  Initialisation de la base et des donnees de demo..."
sleep 12

echo ""
echo "  ========================================"
echo "     NovaBank est prete !"
echo "  ========================================"
echo ""
echo "  Application  :  http://localhost:8090"
echo "  API (Swagger):  http://localhost:8000/docs"
echo ""
echo "  Comptes de demonstration :"
echo "    Directeur   : directeur@novabank.ma  / Directeur@2026!"
echo "    Conseiller  : conseiller@novabank.ma / Conseiller@2026!"
echo "    Admin       : admin@novabank.ma      / Admin@2026!"
echo ""

# Ouvrir le navigateur (macOS: open, Linux: xdg-open)
if command -v open >/dev/null 2>&1; then open http://localhost:8090
elif command -v xdg-open >/dev/null 2>&1; then xdg-open http://localhost:8090
fi
