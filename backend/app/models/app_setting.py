"""Modèle AppSetting — les réglages d'agence modifiables À CHAUD.

Pourquoi une table et pas seulement le fichier .env ?
    Le .env fixe la configuration de DÉPLOIEMENT (immuable sans redémarrer).
    Or certains réglages sont des décisions MÉTIER qui doivent évoluer en
    production sans intervention technique — le seuil d'alerte en tête :
    un directeur qui subit trop de faux positifs doit pouvoir le relever
    lui-même (et cette décision doit être TRACÉE dans l'audit).

    Le .env reste la VALEUR PAR DÉFAUT : la table ne contient que les
    réglages explicitement modifiés (lecture avec repli, jamais de panne).

Format clé/valeur volontairement générique : le prochain réglage d'agence
(langue, délai de verrouillage...) ne demandera AUCUNE migration.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AppSetting(Base):
    __tablename__ = "app_settings"

    # La clé du réglage (ex. "risk_alert_threshold") sert de clé primaire :
    # un réglage = une ligne, l'upsert reste trivial.
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(255))

    # Qui a modifié ce réglage en dernier, et quand — la table porte sa
    # propre mini-traçabilité en plus de l'entrée d'audit détaillée.
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
