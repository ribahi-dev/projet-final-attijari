"""Workflow d'approbation du profil de risque (maker-checker).

Ajoute un statut (none/pending/active) et les auteurs de la demande et de
l'approbation : le conseiller PROPOSE, le directeur APPROUVE. Le calibrage
du scoring ne s'applique que si le statut est 'active'.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_status = sa.Enum("none", "pending", "active", name="risk_profile_status")


def upgrade() -> None:
    _status.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "clients",
        sa.Column("risk_profile_status", _status, nullable=False, server_default="none"),
    )
    op.add_column(
        "clients",
        sa.Column("risk_requested_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column(
        "clients",
        sa.Column("risk_reviewed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("clients", "risk_reviewed_by_id")
    op.drop_column("clients", "risk_requested_by_id")
    op.drop_column("clients", "risk_profile_status")
    _status.drop(op.get_bind(), checkfirst=True)
