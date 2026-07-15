"""Gestion des clients bancaires — Conseiller et Directeur (CdC Module 2)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.session import get_db
from app.models import Client, User
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate, RiskProfileUpdate
from app.services import audit_service

router = APIRouter(prefix="/clients", tags=["Clients"])

# Dépendance partagée : conseiller OU directeur (l'admin gère la plateforme,
# pas la clientèle — séparation des responsabilités du CdC §6.1).
Staff = Annotated[User, Depends(require_role("advisor", "director"))]
# Le profil de risque (qui ASSOUPLIT la détection) est un acte de
# gouvernance -> réservé au directeur.
Director = Annotated[User, Depends(require_role("director"))]


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate, request: Request, db: Annotated[Session, Depends(get_db)], staff: Staff
):
    if db.scalar(select(Client).where(Client.cin == data.cin)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Un client avec ce CIN existe déjà")

    client = Client(**data.model_dump())
    db.add(client)
    db.flush()
    audit_service.log_action(
        db, "client_created", user_id=staff.id, entity_type="client", entity_id=client.id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(client)
    return client


@router.get("", response_model=list[ClientResponse])
def list_clients(
    db: Annotated[Session, Depends(get_db)],
    staff: Staff,
    search: str | None = None,
    include_inactive: bool = False,
    skip: int = 0,
    limit: int = 50,
):
    query = select(Client)
    if not include_inactive:
        query = query.where(Client.is_active.is_(True))
    if search:
        # Recherche par nom, prénom ou CIN (CdC Module 2), insensible à la casse.
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Client.first_name.ilike(pattern),
                Client.last_name.ilike(pattern),
                Client.cin.ilike(pattern),
            )
        )
    return db.scalars(query.order_by(Client.id).offset(skip).limit(min(limit, 100))).all()


@router.get("/risk-requests", response_model=list[ClientResponse])
def list_risk_requests(db: Annotated[Session, Depends(get_db)], director: Director):
    """Les demandes de profil de risque EN ATTENTE d'approbation (directeur).

    Défini AVANT /{client_id} : sinon FastAPI interpréterait "risk-requests"
    comme un identifiant de client (et renverrait 422)."""
    return db.scalars(
        select(Client).where(Client.risk_profile_status == "pending").order_by(Client.id)
    ).all()


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: int, db: Annotated[Session, Depends(get_db)], staff: Staff):
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int, data: ClientUpdate, request: Request,
    db: Annotated[Session, Depends(get_db)], staff: Staff,
):
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")

    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(client, field, value)
    audit_service.log_action(
        db, "client_updated", user_id=staff.id, entity_type="client", entity_id=client.id,
        ip_address=request.client.host if request.client else None,
        details=f"champs modifiés : {', '.join(changes) or 'aucun'}",
    )
    db.commit()
    db.refresh(client)
    return client


def _profile_labels(client: Client) -> str:
    """Libellés lisibles des options actives d'un client (pour l'audit)."""
    actifs = [
        libelle for actif, libelle in (
            (client.frequent_traveler, "voyageur fréquent"),
            (client.high_net_worth, "grande fortune"),
            (client.business_account, "compte professionnel"),
        ) if actif
    ]
    return ", ".join(actifs) or "aucun"


def _ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post("/{client_id}/risk-profile/request", response_model=ClientResponse)
def request_risk_profile(
    client_id: int, data: RiskProfileUpdate, request: Request,
    db: Annotated[Session, Depends(get_db)], staff: Staff,
):
    """Le CONSEILLER (ou le directeur) PROPOSE un profil de risque.

    Workflow maker-checker : la demande passe en « en attente » et n'affecte
    PAS encore le scoring. Elle devra être approuvée par un directeur. Un
    conseiller ne peut donc jamais assouplir la détection seul."""
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")

    client.frequent_traveler = data.frequent_traveler
    client.high_net_worth = data.high_net_worth
    client.business_account = data.business_account
    client.risk_profile_note = data.note
    client.risk_profile_status = "pending"
    client.risk_requested_by_id = staff.id
    client.risk_reviewed_by_id = None

    audit_service.log_action(
        db, "risk_profile_requested", user_id=staff.id, entity_type="client",
        entity_id=client.id, ip_address=_ip(request),
        details=f"profil demandé: {_profile_labels(client)} | motif: {data.note}",
    )
    db.commit()
    db.refresh(client)
    return client


@router.post("/{client_id}/risk-profile/approve", response_model=ClientResponse)
def approve_risk_profile(
    client_id: int, request: Request,
    db: Annotated[Session, Depends(get_db)], director: Director,
):
    """Le DIRECTEUR APPROUVE une demande en attente -> le profil devient
    ACTIF et le scoring en tient compte. Tracé à l'audit (maker-checker)."""
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")
    if client.risk_profile_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Aucune demande de profil en attente"
        )

    client.risk_profile_status = "active"
    client.risk_reviewed_by_id = director.id
    audit_service.log_action(
        db, "risk_profile_approved", user_id=director.id, entity_type="client",
        entity_id=client.id, ip_address=_ip(request),
        details=f"profil approuvé: {_profile_labels(client)} (demandé par #{client.risk_requested_by_id})",
    )
    db.commit()
    db.refresh(client)
    return client


@router.post("/{client_id}/risk-profile/reject", response_model=ClientResponse)
def reject_risk_profile(
    client_id: int, request: Request,
    db: Annotated[Session, Depends(get_db)], director: Director,
):
    """Le DIRECTEUR REJETTE une demande -> le profil reste sans effet."""
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")
    if client.risk_profile_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Aucune demande de profil en attente"
        )

    audit_service.log_action(
        db, "risk_profile_rejected", user_id=director.id, entity_type="client",
        entity_id=client.id, ip_address=_ip(request),
        details=f"profil rejeté: {_profile_labels(client)} (demandé par #{client.risk_requested_by_id})",
    )
    # La demande est annulée : on efface les options et on repasse à "aucun".
    client.frequent_traveler = False
    client.high_net_worth = False
    client.business_account = False
    client.risk_profile_status = "none"
    client.risk_reviewed_by_id = director.id
    db.commit()
    db.refresh(client)
    return client


@router.patch("/{client_id}/risk-profile", response_model=ClientResponse)
def set_risk_profile(
    client_id: int, data: RiskProfileUpdate, request: Request,
    db: Annotated[Session, Depends(get_db)], director: Director,
):
    """Le DIRECTEUR fixe DIRECTEMENT le profil (il est l'approbateur : pas
    besoin de passer par une demande). Le profil est immédiatement ACTIF.
    Tracé à l'audit."""
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")

    client.frequent_traveler = data.frequent_traveler
    client.high_net_worth = data.high_net_worth
    client.business_account = data.business_account
    client.risk_profile_note = data.note
    any_active = data.frequent_traveler or data.high_net_worth or data.business_account
    client.risk_profile_status = "active" if any_active else "none"
    client.risk_reviewed_by_id = director.id

    audit_service.log_action(
        db, "client_risk_profile_changed", user_id=director.id, entity_type="client",
        entity_id=client.id, ip_address=_ip(request),
        details=f"profil (directeur): {_profile_labels(client)} | motif: {data.note}",
    )
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_client(
    client_id: int, request: Request, db: Annotated[Session, Depends(get_db)], staff: Staff
):
    """Suppression LOGIQUE uniquement (CdC Module 2) : le client disparaît
    des listes mais son historique reste intact pour l'audit."""
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client introuvable")
    client.is_active = False
    audit_service.log_action(
        db, "client_deactivated", user_id=staff.id, entity_type="client", entity_id=client.id,
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
