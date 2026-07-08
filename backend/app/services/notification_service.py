"""Service de notification multi-canal (Telegram + email).

Objectif (idée métier) : prévenir immédiatement le directeur d'agence
lorsqu'un événement sensible survient — transaction à risque détectée par
l'IA, ou verrouillage d'un compte après des échecs de connexion répétés.

Trois principes NON NÉGOCIABLES pour un système bancaire :

1. JAMAIS BLOQUANT — l'envoi se fait dans un thread d'arrière-plan.
   L'API répond instantanément ; la notification part en fond. Une banque
   ne fait pas attendre une transaction à cause d'un message Telegram.

2. JAMAIS FATAL — toute erreur d'envoi (réseau, token invalide, SMTP
   injoignable) est capturée et journalisée. Une notification qui échoue
   ne doit JAMAIS faire échouer l'opération bancaire qui l'a déclenchée.

3. DÉGRADATION PROPRE — si aucun canal n'est configuré (pas de token
   Telegram, pas de SMTP), la notification est simplement JOURNALISÉE
   (visible dans `docker logs`). La démonstration fonctionne donc même
   sans identifiants ; en production on renseigne les vrais canaux.

Le thread d'arrière-plan ne touche JAMAIS la base de données (session
SQLAlchemy non thread-safe) : on lui passe uniquement des chaînes déjà
extraites (adresses, identifiants de chat, texte du message).
"""

import json
import logging
import smtplib
import threading
import urllib.parse
import urllib.request
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User

logger = logging.getLogger("novabank.notifications")


def _post_telegram(chat_id: str, text: str) -> None:
    """Envoie un message via l'API Bot de Telegram (simple requête HTTPS)."""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=payload), timeout=8) as resp:
        resp.read()


def _send_email(to: str, subject: str, body: str) -> None:
    """Envoie un email via SMTP (avec STARTTLS et authentification)."""
    msg = EmailMessage()
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)


def _deliver(subject: str, message: str, email_to: str | None, telegram_chat_id: str | None) -> None:
    """Corps du thread d'arrière-plan : tente chaque canal, journalise le bilan."""
    delivered: list[str] = []
    chat = telegram_chat_id or settings.telegram_chat_id

    if settings.telegram_bot_token and chat:
        try:
            _post_telegram(chat, f"🔔 {subject}\n\n{message}")
            delivered.append("telegram")
        except Exception as exc:  # jamais fatal
            logger.warning("Notification Telegram échouée : %s", exc)

    if settings.smtp_host and email_to:
        try:
            _send_email(email_to, subject, message)
            delivered.append("email")
        except Exception as exc:  # jamais fatal
            logger.warning("Notification email échouée : %s", exc)

    if delivered:
        logger.info("Notification envoyée via %s — %s", ", ".join(delivered), subject)
    else:
        # Aucun canal configuré ou disponible : on trace pour la démo.
        logger.info("[NOTIFICATION] %s | %s (email=%s, telegram=%s)", subject, message, email_to, chat)


def notify(subject: str, message: str, *, email_to: str | None = None, telegram_chat_id: str | None = None) -> None:
    """Déclenche une notification NON BLOQUANTE. Ne lève jamais d'exception."""
    if not settings.notifications_enabled:
        return
    threading.Thread(
        target=_deliver, args=(subject, message, email_to, telegram_chat_id), daemon=True
    ).start()


def fetch_latest_telegram_chat() -> dict | None:
    """Récupère le chat Telegram le plus récent ayant écrit au bot.

    Sert à l'« auto-liaison » : l'utilisateur envoie /start à son bot, puis
    l'application appelle getUpdates et capte son chat_id automatiquement —
    plus besoin de @userinfobot ni de copier l'identifiant à la main.

    Retourne {"chat_id": "...", "name": "..."} ou None (aucun message, pas
    de token, ou erreur réseau — jamais d'exception propagée).
    """
    if not settings.telegram_bot_token:
        return None
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getUpdates"
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.load(resp)
    except Exception as exc:
        logger.warning("Telegram getUpdates échoué : %s", exc)
        return None
    if not data.get("ok"):
        return None
    for update in reversed(data.get("result", [])):
        msg = update.get("message") or update.get("edited_message")
        if msg and "chat" in msg:
            chat = msg["chat"]
            name = chat.get("first_name") or chat.get("title") or chat.get("username") or "Telegram"
            return {"chat_id": str(chat["id"]), "name": name}
    return None


def notify_directors(db: Session, subject: str, message: str) -> None:
    """Prévient tous les directeurs d'agence actifs (chacun sur ses canaux).

    Les contacts sont extraits ICI (dans le thread de la requête), puis
    l'envoi part en arrière-plan avec de simples chaînes — la session `db`
    n'est jamais utilisée hors de ce thread.
    """
    directors = db.scalars(
        select(User).where(User.role == "director", User.is_active.is_(True))
    ).all()
    recipients = [(d.email, d.telegram_chat_id) for d in directors]

    if not recipients:
        notify(subject, message)  # canal agence global (settings) ou journalisation
        return
    for email, telegram_chat_id in recipients:
        notify(subject, message, email_to=email, telegram_chat_id=telegram_chat_id)
