"""Profil de risque client (calibrage du scoring par client).

Ajoute 3 indicateurs + un motif sur la table clients : le directeur peut
neutraliser certains signaux quand ils n'ont pas de sens pour un client
donne (voyageur frequent, grande fortune, compte professionnel). Chaque
changement est tracable et audite.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("frequent_traveler", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "clients",
        sa.Column("high_net_worth", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "clients",
        sa.Column("business_account", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("clients", sa.Column("risk_profile_note", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("clients", "risk_profile_note")
    op.drop_column("clients", "business_account")
    op.drop_column("clients", "high_net_worth")
    op.drop_column("clients", "frequent_traveler")
