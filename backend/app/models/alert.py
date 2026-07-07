"""Modèle Alert — l'alerte levée automatiquement, traitée par le directeur.

Rôle dans le domaine (cahier des charges, Module 9) :
    Deux origines possibles :
      - transaction_risk : le score IA a dépassé le seuil ;
      - login_security  : échecs de connexion répétés / accès suspect.
    Le directeur consulte l'alerte, lit l'explication du score associé,
    puis la qualifie et la clôture — c'est le "cycle de vie de l'alerte"
    du diagramme d'activité UML (cahier des charges §7.4).

Choix techniques à retenir :
    - transaction_id NULLABLE : une alerte de sécurité (login) n'est liée
      à aucune transaction. C'est le nullable qui encode cette règle métier.
    - closed_at séparé de created_at : permet de mesurer le TEMPS DE
      TRAITEMENT des alertes — un vrai KPI du dashboard directeur.
    - status open/in_progress/closed : machine à états simple ; le service
      métier (Phase B) refusera les transitions invalides (closed -> open).
"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)

    alert_type: Mapped[str] = mapped_column(
        Enum("transaction_risk", "login_security", name="alert_type"),
    )

    level: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", "critical", name="alert_level"),
        default="medium",
    )

    message: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        Enum("open", "in_progress", "closed", name="alert_status"),
        default="open",
    )

    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"))

    # BOUCLE DE FEEDBACK (cœur de la version PFE) : en clôturant, le
    # directeur qualifie l'alerte. Ces qualifications sont les ÉTIQUETTES
    # d'entraînement du modèle ML — le système apprend des décisions
    # humaines de l'agence (human-in-the-loop), là où les solutions
    # commerciales exigent des données étiquetées externes.
    resolution: Mapped[str | None] = mapped_column(
        Enum("confirmed_fraud", "false_positive", name="alert_resolution")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    transaction = relationship("Transaction", back_populates="alerts")
