"""Endpoints de gestion des notifications Telegram (liaison + test).

Confort « pro » pour la soutenance : plutôt que de chercher son chat_id via
@userinfobot et de le copier, l'utilisateur envoie /start à son bot puis
clique « Lier mon Telegram » — l'application capte l'identifiant toute seule.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import CurrentUser
from app.db.session import get_db
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/telegram/link-me")
def link_my_telegram(current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]):
    """Capte automatiquement le chat_id de l'utilisateur et l'enregistre.

    Pré-requis : avoir envoyé un message (ex. /start) au bot juste avant.
    """
    if not settings.telegram_bot_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun bot Telegram configuré (TELEGRAM_BOT_TOKEN manquant).",
        )
    info = notification_service.fetch_latest_telegram_chat()
    if info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun message reçu par le bot. Envoyez '/start' à votre bot puis réessayez.",
        )
    current_user.telegram_chat_id = info["chat_id"]
    db.commit()
    return {"telegram_chat_id": info["chat_id"], "name": info["name"]}


@router.post("/test")
def send_test_notification(current_user: CurrentUser):
    """Envoie une notification de test à l'utilisateur connecté."""
    chat = current_user.telegram_chat_id or settings.telegram_chat_id
    if not (settings.telegram_bot_token and chat) and not settings.smtp_host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun canal de notification configuré (Telegram ou email).",
        )
    notification_service.notify(
        "✅ Test NovaBank",
        "Ceci est une notification de test. Si vous la recevez, tout fonctionne !",
        email_to=current_user.email,
        telegram_chat_id=current_user.telegram_chat_id,
    )
    return {"status": "envoyé"}
