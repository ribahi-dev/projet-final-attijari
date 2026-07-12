"""Réglages d'agence — le directeur pilote la sensibilité de la détection.

Le seuil d'alerte est LA molette de gouvernance du dispositif :
    seuil bas  -> plus d'alertes, moins de fraudes ratées, plus de travail ;
    seuil haut -> moins de bruit, mais risque de laisser passer.
La page « Santé du modèle » donne les chiffres (précision, faux positifs)
qui ÉCLAIRENT ce choix — ici, le directeur l'applique.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models import User
from app.services import agency_settings_service

router = APIRouter(
    prefix="/agency-settings",
    tags=["Réglages d'agence"],
    dependencies=[Depends(require_role("director"))],
)


class AlertThresholdResponse(BaseModel):
    threshold: int
    # True si la valeur vient d'une décision du directeur (table), False si
    # c'est encore le défaut du déploiement (.env) — l'UI l'affiche.
    overridden: bool


class AlertThresholdUpdate(BaseModel):
    threshold: int = Field(ge=1, le=100)


@router.get("/alert-threshold", response_model=AlertThresholdResponse)
def read_alert_threshold(db: Annotated[Session, Depends(get_db)]):
    return AlertThresholdResponse(
        threshold=agency_settings_service.get_risk_threshold(db),
        overridden=agency_settings_service.is_threshold_overridden(db),
    )


@router.patch("/alert-threshold", response_model=AlertThresholdResponse)
def update_alert_threshold(
    payload: AlertThresholdUpdate, request: Request,
    db: Annotated[Session, Depends(get_db)],
    director: Annotated[User, Depends(require_role("director"))],
):
    try:
        agency_settings_service.set_risk_threshold(
            db, payload.threshold, user_id=director.id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as exc:  # défense en profondeur (Pydantic borne déjà)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    db.commit()
    return AlertThresholdResponse(
        threshold=agency_settings_service.get_risk_threshold(db), overridden=True
    )
