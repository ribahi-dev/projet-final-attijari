"""Modèle Client — le client bancaire (simulé) de l'agence.

Rôle dans le domaine (cahier des charges, Module 2) :
    Un client possède un ou plusieurs comptes ; le conseiller peut le
    rechercher par nom ou CIN, consulter sa fiche, et le DÉSACTIVER
    (suppression logique via is_active — jamais de DELETE physique :
    l'historique bancaire doit rester intact pour l'audit).

Choix techniques à retenir :
    - Numeric(12, 2) pour l'argent, JAMAIS Float : un float binaire ne sait
      pas représenter 0.10 exactement — les erreurs d'arrondi s'accumulent,
      inacceptable en banque. Numeric = décimal exact.
    - server_default=func.now() : l'horodatage est produit par POSTGRESQL,
      pas par Python. Une seule horloge de référence pour tout le système
      (deux serveurs API auraient deux horloges légèrement différentes).
    - `Mapped[str | None]` = colonne NULLABLE ; `Mapped[str]` = NOT NULL.
      Le type Python déclare l'intention, SQLAlchemy génère la contrainte.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Client(Base):
    __tablename__ = "clients"

    # primary_key=True crée déjà un index unique — inutile d'ajouter index=True.
    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    # CIN = identifiant national marocain, unique par personne (exigence KYC).
    # index=True car c'est LE critère de recherche du conseiller (Module 2).
    cin: Mapped[str] = mapped_column(String(30), unique=True, index=True)

    phone: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(255))

    # Profession et revenu : features importantes pour le module IA
    # (écart entre le montant d'une transaction et le profil du client).
    profession: Mapped[str | None] = mapped_column(String(100))
    monthly_income: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # PROFIL DE RISQUE (calibrage du scoring PAR CLIENT). Le directeur peut
    # neutraliser certains signaux quand ils n'ont pas de sens pour CE client :
    #   - frequent_traveler : un businessman qui se déplace -> le changement de
    #     ville n'est pas suspect (neutralise city_changed) ;
    #   - high_net_worth : une grande fortune -> le revenu mensuel déclaré ne
    #     reflète pas sa capacité (neutralise les ratios montant/revenu) ;
    #   - business_account : une entreprise -> un gros volume d'opérations est
    #     normal (neutralise la rafale tx_24h).
    # ⚠️ Assouplir un contrôle est EN SOI un risque (mécanisme classique de la
    # fraude interne) : chaque changement exige un motif et est tracé à l'audit.
    frequent_traveler: Mapped[bool] = mapped_column(Boolean, default=False)
    high_net_worth: Mapped[bool] = mapped_column(Boolean, default=False)
    business_account: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_profile_note: Mapped[str | None] = mapped_column(String(255))

    # WORKFLOW MAKER-CHECKER (séparation des tâches / principe des 4 yeux) :
    # le CONSEILLER propose un profil, le DIRECTEUR l'approuve. Le calibrage
    # du scoring ne s'applique QUE si le statut est "active" -> un conseiller
    # ne peut jamais assouplir la détection seul (parade à la fraude interne).
    #   none    : aucun profil
    #   pending : proposé par un conseiller, en attente d'approbation
    #   active  : approuvé (ou fixé directement par le directeur)
    risk_profile_status: Mapped[str] = mapped_column(
        Enum("none", "pending", "active", name="risk_profile_status"), default="none"
    )
    # Qui a proposé (conseiller) et qui a approuvé (directeur) — traçabilité.
    risk_requested_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    risk_reviewed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    # Suppression logique : un client désactivé disparaît des écrans mais
    # reste en base (intégrité référentielle + audit réglementaire).
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relation 1-N : UN client possède PLUSIEURS comptes.
    # back_populates lie les deux sens : client.accounts <-> account.client.
    # C'est un attribut Python (navigation objet), pas une colonne SQL —
    # la clé étrangère, elle, vit côté Account (accounts.client_id).
    accounts = relationship("Account", back_populates="client")
