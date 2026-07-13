#!/usr/bin/env bash
# =============================================================================
#  NovaBank - Reconstruire les images (macOS / Linux)
#
#  A utiliser UNIQUEMENT apres avoir modifie le code : force la reconstruction
#  des images Docker (internet requis la 1ere fois). Pour un simple demarrage,
#  utiliser "./demarrer.sh" qui reutilise les images deja construites.
# =============================================================================
cd "$(dirname "$0")"

echo ""
echo "  ========================================"
echo "     NovaBank - Reconstruction des images"
echo "  ========================================"
echo ""

if ! docker info >/dev/null 2>&1; then
  echo "  [ERREUR] Docker n'est pas demarre. Lance Docker Desktop puis reessaie."
  exit 1
fi

echo "  Reconstruction (connexion internet requise)..."
echo ""
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
echo "  Images reconstruites et services redemarres."
echo "  Application : http://localhost:8090"
echo ""
