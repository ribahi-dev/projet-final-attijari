#!/usr/bin/env bash
# =============================================================================
#  NovaBank - Reconstruire + REINITIALISER (macOS / Linux)
#
#  A utiliser apres avoir MIS A JOUR LE CODE (nouveau ZIP / git pull) :
#   - reconstruit les images depuis le code present ;
#   - REINITIALISE la base (indispensable si le schema a change : nouvelles
#     colonnes) puis re-injecte les donnees de demonstration.
#
#  La base est remise a zero (donnees simulees recreees). Pour un simple
#  demarrage sans reset, utiliser "./demarrer.sh".
# =============================================================================
cd "$(dirname "$0")"

echo ""
echo "  ========================================"
echo "     NovaBank - Reconstruction + reset base"
echo "  ========================================"
echo ""

if ! docker info >/dev/null 2>&1; then
  echo "  [ERREUR] Docker n'est pas demarre. Lance Docker Desktop puis reessaie."
  exit 1
fi

echo "  Reinitialisation de la base + reconstruction depuis le code..."
echo "  (les donnees de demo seront recreees automatiquement)"
echo ""
# down -v : supprime AUSSI le volume de la base -> tables recreees avec le
# schema A JOUR (corrige "colonne manquante" apres une mise a jour du code).
docker compose down -v --remove-orphans >/dev/null 2>&1 || true
for c in $(docker ps -q --filter "publish=8090" --filter "publish=8000" --filter "publish=5433" 2>/dev/null); do
  docker stop "$c" >/dev/null 2>&1 || true
done
# up -d --build : reconstruit depuis le code (cache -> rapide et hors-ligne).
if ! docker compose up -d --build; then
  echo ""
  echo "  [INFO] Echec (telechargement d'image interrompu ?). Nouvelle tentative..."
  sleep 8
  if ! docker compose up -d --build; then
    echo ""
    echo "  [ERREUR] La reconstruction a echoue -- souvent un probleme de connexion"
    echo "  pour telecharger les images de base. Verifie internet et relance."
    exit 1
  fi
fi

echo ""
echo "  Base reinitialisee et services redemarres."
echo "  Application : http://localhost:8090"
echo ""

if command -v open >/dev/null 2>&1; then open http://localhost:8090
elif command -v xdg-open >/dev/null 2>&1; then xdg-open http://localhost:8090
fi
