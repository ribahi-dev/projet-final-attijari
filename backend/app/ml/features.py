"""Extraction des features de risque d'une transaction.

Les 7 signaux, transformés en nombres pour le modèle :

    amount_over_income    : montant / revenu mensuel du client (0 si inconnu)
    amount_over_avg       : montant / moyenne historique du compte (0 si vide)
    is_night              : 1 si l'opération a lieu entre 00h et 06h
    city_changed          : 1 si la ville diffère de la précédente opération
    tx_last_24h           : nombre d'opérations du compte sur 24h glissantes
    cumul_72h_over_income : cumul des montants sur 72h / revenu mensuel
                            -> détecte le FRACTIONNEMENT (structuring) : des
                            petits montants isolés paraissent normaux, mais
                            leur SOMME sur 72h trahit le contournement de seuil.
    days_since_last_tx    : jours depuis la dernière opération du compte
                            -> détecte la RÉACTIVATION d'un compte DORMANT,
                            schéma classique d'usurpation / compte compromis.

Règle d'or : cette fonction est LA définition des features. L'entraînement
(scripts/train_model.py) et l'inférence (scoring_service) l'importent tous
les deux — jamais deux implémentations parallèles.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Account, Transaction

# Ordre CANONIQUE des features — celui des colonnes vues par le modèle.
FEATURE_NAMES = [
    "amount_over_income",
    "amount_over_avg",
    "is_night",
    "city_changed",
    "tx_last_24h",
    "cumul_72h_over_income",
    "days_since_last_tx",
]


@dataclass
class TransactionFeatures:
    amount_over_income: float
    amount_over_avg: float
    is_night: int
    city_changed: int
    tx_last_24h: int
    cumul_72h_over_income: float = 0.0
    days_since_last_tx: int = 0

    def as_vector(self) -> list[float]:
        d = asdict(self)
        return [float(d[name]) for name in FEATURE_NAMES]


def extract_features(
    db: Session,
    account: Account,
    amount: Decimal,
    city: str | None,
    moment: datetime | None = None,
) -> TransactionFeatures:
    """Calcule les features AVANT insertion de la transaction analysée
    (l'historique interrogé ne doit pas contenir l'opération en cours)."""
    moment = moment or datetime.now(timezone.utc)

    income = account.client.monthly_income if account.client else None
    amount_over_income = float(amount / income) if income and income > 0 else 0.0

    avg = db.scalar(select(func.avg(Transaction.amount)).where(Transaction.account_id == account.id))
    amount_over_avg = float(amount / avg) if avg and avg > 0 else 0.0

    local_hour = moment.astimezone().hour if moment.tzinfo else moment.hour
    is_night = 1 if 0 <= local_hour < 6 else 0

    city_changed = 0
    if city:
        last_city = db.scalar(
            select(Transaction.city)
            .where(Transaction.account_id == account.id, Transaction.city.is_not(None))
            .order_by(Transaction.created_at.desc())
            .limit(1)
        )
        if last_city and last_city.strip().lower() != city.strip().lower():
            city_changed = 1

    tx_last_24h = db.scalar(
        select(func.count())
        .select_from(Transaction)
        .where(
            Transaction.account_id == account.id,
            Transaction.created_at >= moment - timedelta(hours=24),
        )
    ) or 0

    # Cumul 72h (fractionnement) — la somme INCLUT l'opération courante :
    # c'est le total qui trahit le contournement, pas le montant isolé.
    since_72h = moment - timedelta(hours=72)
    sum_72h = db.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.account_id == account.id,
            Transaction.created_at >= since_72h,
        )
    ) or Decimal(0)
    total_72h = Decimal(sum_72h) + amount
    cumul_72h_over_income = float(total_72h / income) if income and income > 0 else 0.0

    # Jours depuis la dernière opération (compte dormant réactivé).
    # Plafonné à 365 : au-delà, l'information n'augmente plus le risque.
    last_tx_date = db.scalar(
        select(func.max(Transaction.created_at)).where(Transaction.account_id == account.id)
    )
    if last_tx_date is not None:
        m = moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)
        lt = last_tx_date if last_tx_date.tzinfo else last_tx_date.replace(tzinfo=timezone.utc)
        days_since_last_tx = min(365, max(0, (m - lt).days))
    else:
        days_since_last_tx = 0

    return TransactionFeatures(
        amount_over_income=amount_over_income,
        amount_over_avg=amount_over_avg,
        is_night=is_night,
        city_changed=city_changed,
        tx_last_24h=int(tx_last_24h),
        cumul_72h_over_income=cumul_72h_over_income,
        days_since_last_tx=days_since_last_tx,
    )


def explain_features(f: TransactionFeatures) -> list[str]:
    """Traduit les features en raisons LISIBLES (exigence d'explicabilité,
    CdC §9.2). Utilisé par le moteur de règles ET par le modèle ML :
    l'explication reste compréhensible par un directeur d'agence."""
    reasons: list[str] = []
    if f.amount_over_income >= 1:
        reasons.append(f"montant {f.amount_over_income:.1f}x supérieur au revenu mensuel du client")
    elif f.amount_over_income >= 0.5:
        reasons.append("montant représentant plus de la moitié du revenu mensuel")
    if f.amount_over_avg >= 3:
        reasons.append(f"montant {f.amount_over_avg:.1f}x supérieur à la moyenne du compte")
    if f.is_night:
        reasons.append("opération nocturne, hors des horaires habituels")
    if f.city_changed:
        reasons.append("ville inhabituelle par rapport aux opérations précédentes")
    if f.tx_last_24h >= 5:
        reasons.append(f"{f.tx_last_24h} opérations sur les dernières 24h")
    if f.cumul_72h_over_income >= 1.5:
        reasons.append(
            f"cumul des opérations sur 72h élevé ({f.cumul_72h_over_income:.1f}x le revenu)"
            " — possible fractionnement"
        )
    if f.days_since_last_tx >= 90:
        reasons.append(f"compte dormant réactivé (aucune opération depuis {f.days_since_last_tx} jours)")
    elif f.days_since_last_tx >= 30:
        reasons.append(f"compte peu actif ({f.days_since_last_tx} jours d'inactivité)")
    return reasons
