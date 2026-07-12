"""Dashboard directeur : KPI, tendances, répartition (CdC Modules 5 et 6).

Les agrégations sont faites PAR POSTGRESQL (func.count/sum/avg) : on ne
rapatrie jamais des milliers de lignes pour les additionner en Python.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models import Account, Alert, AuditLog, Client, RiskScore, Transaction, User
from app.schemas.analytics import (
    AdvisorActivity, InternalMonitoringResponse, KpiResponse, ModelHealthResponse,
    ScoreBucket, TrendPoint, TypeDistribution,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(require_role("director"))],
)

ZERO = Decimal("0")


@router.get("/kpi", response_model=KpiResponse)
def get_kpi(db: Annotated[Session, Depends(get_db)]):
    sums = db.execute(
        select(
            func.coalesce(
                func.sum(Transaction.amount).filter(Transaction.transaction_type == "deposit"), ZERO
            ),
            func.coalesce(
                func.sum(Transaction.amount).filter(Transaction.transaction_type == "withdrawal"), ZERO
            ),
        )
    ).one()

    return KpiResponse(
        total_clients=db.scalar(select(func.count()).select_from(Client).where(Client.is_active.is_(True))),
        total_accounts=db.scalar(select(func.count()).select_from(Account)),
        total_transactions=db.scalar(select(func.count()).select_from(Transaction)),
        open_alerts=db.scalar(select(func.count()).select_from(Alert).where(Alert.status == "open")),
        total_deposits=sums[0],
        total_withdrawals=sums[1],
        average_risk_score=db.scalar(select(func.avg(RiskScore.score))),
    )


@router.get("/trends", response_model=list[TrendPoint])
def get_trends(db: Annotated[Session, Depends(get_db)], days: int = 30):
    since = datetime.now(timezone.utc) - timedelta(days=min(days, 365))
    day = func.date_trunc("day", Transaction.created_at).label("day")
    rows = db.execute(
        select(day, func.count().label("n"), func.sum(Transaction.amount).label("total"))
        .where(Transaction.created_at >= since)
        .group_by(day)
        .order_by(day)
    ).all()
    return [
        TrendPoint(day=row.day.date(), transaction_count=row.n, total_amount=row.total or ZERO)
        for row in rows
    ]


@router.get("/internal-monitoring", response_model=InternalMonitoringResponse)
def get_internal_monitoring(db: Annotated[Session, Depends(get_db)]):
    """Surveillance de la fraude INTERNE : le comportement des conseillers.

    Indicateurs par conseiller, agrégés côté PostgreSQL depuis les
    transactions et le journal d'audit (append-only : l'employé ne peut pas
    effacer ses traces). Les anomalies sont des drapeaux EXPLICABLES —
    ils désignent un comportement à examiner, jamais une culpabilité.
    """
    advisors = db.scalars(
        select(User).where(User.role == "advisor", User.is_active.is_(True))
    ).all()

    # Volume, nombre et opérations nocturnes par conseiller, en une requête.
    # timezone('Africa/Casablanca') convertit l'horodatage UTC en heure
    # locale de l'agence — la même notion de "nuit" que le scoring client.
    local_hour = func.extract("hour", func.timezone("Africa/Casablanca", Transaction.created_at))
    activity = {
        row.uid: row
        for row in db.execute(
            select(
                Transaction.created_by_id.label("uid"),
                func.count().label("n"),
                func.coalesce(func.sum(Transaction.amount), ZERO).label("total"),
                func.count().filter(local_hour < 6).label("night"),
            ).group_by(Transaction.created_by_id)
        ).all()
    }

    # Opérations à haut risque (score >= 70) par conseiller.
    high_risk = dict(
        db.execute(
            select(Transaction.created_by_id, func.count())
            .join(RiskScore, RiskScore.transaction_id == Transaction.id)
            .where(RiskScore.score >= 70)
            .group_by(Transaction.created_by_id)
        ).all()
    )

    # Concentration : le nombre maximal d'opérations sur UN même compte.
    per_account = (
        select(
            Transaction.created_by_id.label("uid"),
            func.count().label("c"),
        )
        .group_by(Transaction.created_by_id, Transaction.account_id)
        .subquery()
    )
    concentration = dict(
        db.execute(
            select(per_account.c.uid, func.max(per_account.c.c)).group_by(per_account.c.uid)
        ).all()
    )

    # Échecs de connexion (journal d'audit).
    failed = dict(
        db.execute(
            select(AuditLog.user_id, func.count())
            .where(AuditLog.action == "login_failed", AuditLog.user_id.is_not(None))
            .group_by(AuditLog.user_id)
        ).all()
    )

    # Référence des pairs : volume moyen des conseillers ACTIFS (>= 1 op).
    totals = [Decimal(activity[a.id].total) for a in advisors if a.id in activity]
    peer_avg = sum(totals) / len(totals) if totals else ZERO

    result: list[AdvisorActivity] = []
    for a in advisors:
        row = activity.get(a.id)
        n = row.n if row else 0
        total = Decimal(row.total) if row else ZERO
        night = row.night if row else 0
        risky = high_risk.get(a.id, 0)
        concentrated = concentration.get(a.id, 0)
        fails = failed.get(a.id, 0)

        flags: list[str] = []
        if night >= 3:
            flags.append(f"{night} opérations saisies de nuit (00h-06h)")
        if len(totals) >= 2 and total > 2 * peer_avg:
            flags.append(
                f"volume traité {float(total / peer_avg):.1f}x supérieur à la moyenne des pairs"
            )
        if concentrated >= 10:
            flags.append(f"{concentrated} opérations concentrées sur un même compte")
        if n >= 5 and risky / n >= 0.3:
            flags.append(f"{risky} opérations à haut risque sur {n} saisies")
        if fails >= 5:
            flags.append(f"{fails} échecs de connexion enregistrés")

        result.append(AdvisorActivity(
            user_id=a.id, name=f"{a.first_name} {a.last_name}",
            tx_count=n, total_amount=total, night_count=night,
            high_risk_count=risky, max_ops_same_account=concentrated,
            failed_logins=fails, flags=flags, is_anomalous=bool(flags),
        ))

    # Les profils à examiner d'abord, puis par volume décroissant.
    result.sort(key=lambda r: (not r.is_anomalous, -r.total_amount))
    return InternalMonitoringResponse(advisors=result, peer_avg_amount=peer_avg)


@router.get("/model-health", response_model=ModelHealthResponse)
def get_model_health(db: Annotated[Session, Depends(get_db)]):
    """Suivi de la fraude & santé du modèle (MLOps).

    Toutes les métriques sont calculées sur les QUALIFICATIONS HUMAINES
    (boucle de feedback) : c'est la performance réelle vécue par l'agence,
    pas celle du jeu de test d'entraînement.
    """
    # Décomptes des alertes transactionnelles qualifiées, en UNE requête.
    confirmed, false_pos = db.execute(
        select(
            func.count().filter(Alert.resolution == "confirmed_fraud"),
            func.count().filter(Alert.resolution == "false_positive"),
        ).where(Alert.alert_type == "transaction_risk")
    ).one()
    processed = confirmed + false_pos

    # Temps moyen de traitement d'une alerte (création -> clôture), en heures.
    avg_seconds = db.scalar(
        select(func.avg(func.extract("epoch", Alert.closed_at - Alert.created_at))).where(
            Alert.closed_at.is_not(None)
        )
    )

    # Histogramme des scores par tranche de 10 (le score 100 rejoint la
    # tranche 90-100 via LEAST) — l'agrégation reste côté PostgreSQL.
    bucket = func.least(func.floor(RiskScore.score / 10) * 10, 90).label("bucket")
    rows = db.execute(select(bucket, func.count()).group_by(bucket).order_by(bucket)).all()

    return ModelHealthResponse(
        model_version=db.scalar(
            select(RiskScore.model_version).order_by(RiskScore.created_at.desc()).limit(1)
        ),
        total_scored=db.scalar(select(func.count()).select_from(RiskScore)),
        open_alerts=db.scalar(
            select(func.count()).select_from(Alert).where(Alert.status != "closed")
        ),
        alerts_processed=processed,
        confirmed_fraud=confirmed,
        false_positives=false_pos,
        precision_production=confirmed / processed if processed else None,
        false_positive_rate=false_pos / processed if processed else None,
        feedback_available=processed,
        avg_processing_hours=float(avg_seconds) / 3600 if avg_seconds is not None else None,
        score_distribution=[ScoreBucket(range_start=int(r[0]), count=r[1]) for r in rows],
    )


@router.get("/distribution", response_model=list[TypeDistribution])
def get_type_distribution(db: Annotated[Session, Depends(get_db)]):
    rows = db.execute(
        select(
            Transaction.transaction_type,
            func.count().label("n"),
            func.sum(Transaction.amount).label("total"),
        ).group_by(Transaction.transaction_type)
    ).all()
    return [
        TypeDistribution(transaction_type=row.transaction_type, count=row.n, total_amount=row.total or ZERO)
        for row in rows
    ]
