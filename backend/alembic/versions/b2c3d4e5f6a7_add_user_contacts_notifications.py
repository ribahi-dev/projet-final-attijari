"""add user contacts for notifications (phone, telegram_chat_id)

Ajoute les coordonnées de notification sur la table users : le directeur
d'agence peut être joint par téléphone (affichage) et par Telegram lorsqu'une
transaction à risque ou un verrouillage de compte est détecté.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-08
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(length=30), nullable=True))
    op.add_column("users", sa.Column("telegram_chat_id", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "telegram_chat_id")
    op.drop_column("users", "phone")
