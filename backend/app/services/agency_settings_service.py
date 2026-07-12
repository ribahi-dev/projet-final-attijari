"""Réglages d'agence — lecture avec repli, écriture auditée.

Règle de la couche service : aucune logique HTTP ici. Le router traduit
les erreurs métier (ValueError) en codes HTTP.
"""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import AppSetting
from app.services import audit_service

RISK_THRESHOLD_KEY = "risk_alert_threshold"


def get_risk_threshold(db: Session) -> int:
    """Seuil d'alerte effectif : la valeur décidée par le directeur si elle
    existe, sinon la valeur par défaut du déploiement (.env). Le repli
    garantit que le scoring n'est JAMAIS bloqué par un réglage manquant."""
    row = db.get(AppSetting, RISK_THRESHOLD_KEY)
    if row is not None:
        try:
            return int(row.value)
        except ValueError:  # valeur corrompue -> on retombe sur le défaut
            pass
    return settings.risk_alert_threshold


def is_threshold_overridden(db: Session) -> bool:
    return db.get(AppSetting, RISK_THRESHOLD_KEY) is not None


def set_risk_threshold(
    db: Session, value: int, *, user_id: int, ip_address: str | None
) -> int:
    """Modifie le seuil (1-100) et TRACE la décision : changer la
    sensibilité de la détection de fraude est un acte de gouvernance,
    pas un détail technique."""
    if not 1 <= value <= 100:
        raise ValueError("Le seuil doit être compris entre 1 et 100")

    previous = get_risk_threshold(db)
    row = db.get(AppSetting, RISK_THRESHOLD_KEY)
    if row is None:
        row = AppSetting(key=RISK_THRESHOLD_KEY, value=str(value), updated_by_id=user_id)
        db.add(row)
    else:
        row.value = str(value)
        row.updated_by_id = user_id

    audit_service.log_action(
        db, "alert_threshold_changed", user_id=user_id, entity_type="app_setting",
        ip_address=ip_address,
        details=f"seuil d'alerte modifié : {previous} -> {value}",
    )
    return value
