"""Point d'entrée de l'API NovaBank : assemblage de l'application.

Ce fichier ne fait QUE brancher (routers, CORS) — aucune logique métier.
Documentation interactive : /docs (Swagger) et /redoc.
Lancement dev : uvicorn app.main:app --reload
"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    accounts, agency_settings, alerts, analytics, audit, auth, clients,
    notifications, reports, transactions, users,
)

# Logging applicatif : on garantit que les logs "novabank.*" (notamment les
# notifications) apparaissent sur la sortie standard — donc dans `docker logs`.
# Sans cette config, les messages INFO de nos loggers seraient filtrés par la
# configuration par défaut d'uvicorn.
_app_logger = logging.getLogger("novabank")
if not _app_logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    _app_logger.addHandler(_handler)
    _app_logger.setLevel(logging.INFO)
    _app_logger.propagate = False

app = FastAPI(
    title=settings.app_name,
    description="Plateforme bancaire intelligente d'aide à la décision — détection "
    "d'anomalies par Machine Learning (Random Forest + SHAP)",
    version="2.0.0",
)

# CORS : seul le frontend de dev est autorisé (liste blanche stricte,
# jamais '*' quand les requêtes portent un jeton d'authentification).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clients.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(agency_settings.router)
app.include_router(reports.router)
app.include_router(notifications.router)
app.include_router(audit.router)


@app.get("/health", tags=["Supervision"])
def health_check():
    """Sonde de vie pour Docker/monitoring — ne touche pas la base."""
    return {"status": "ok", "app": settings.app_name}
