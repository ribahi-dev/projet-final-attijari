"""Schemas du dashboard directeur (Modules 5 et 6 du cahier des charges)."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class KpiResponse(BaseModel):
    total_clients: int
    total_accounts: int
    total_transactions: int
    open_alerts: int
    total_deposits: Decimal
    total_withdrawals: Decimal
    average_risk_score: float | None  # None tant qu'aucune transaction scorée


class TrendPoint(BaseModel):
    day: date
    transaction_count: int
    total_amount: Decimal


class TypeDistribution(BaseModel):
    transaction_type: str
    count: int
    total_amount: Decimal


class ScoreBucket(BaseModel):
    """Une tranche de l'histogramme des scores (0-9, 10-19, ..., 90-100)."""

    range_start: int
    count: int


class ModelHealthResponse(BaseModel):
    """Suivi de la fraude & santé du modèle (MLOps, s'inspire du «Suivi de
    la fraude» publié par Bank Al-Maghrib).

    Le principe : un modèle de fraude se DÉGRADE avec le temps (les
    fraudeurs s'adaptent — dérive conceptuelle). On surveille donc sa
    performance RÉELLE en production, calculée sur les qualifications
    humaines du directeur — pas sur le jeu de test d'origine.
    """

    model_version: str | None       # moteur ayant produit le dernier score
    total_scored: int               # transactions passées au scoring
    open_alerts: int                # alertes en attente de traitement
    alerts_processed: int           # alertes transactionnelles QUALIFIÉES
    confirmed_fraud: int            # ... dont fraudes confirmées
    false_positives: int            # ... dont faux positifs
    # Précision réelle en production = confirmées / qualifiées. C'est LA
    # métrique de santé : si elle chute, le modèle crie au loup pour rien.
    precision_production: float | None
    false_positive_rate: float | None
    # Volume d'étiquettes accumulées pour le prochain réentraînement.
    feedback_available: int
    avg_processing_hours: float | None  # réactivité du traitement des alertes
    score_distribution: list[ScoreBucket]
