"""alert resolution feedback loop

Ajoute alerts.resolution : la qualification du directeur à la clôture
(confirmed_fraud / false_positive), étiquette d'entraînement du modèle ML.

⚠️ Correction manuelle vs le code auto-généré : sur PostgreSQL,
op.add_column ne crée PAS le type ENUM référencé — il faut le créer
explicitement avant (et le supprimer au downgrade). C'est LE piège
classique d'Alembic avec les enums natifs, à connaître en entretien.

Revision ID: 55c4f769e4c7
Revises: f5e8beaf989d
Create Date: 2026-07-07 09:27:52.069236

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '55c4f769e4c7'
down_revision: Union[str, Sequence[str], None] = 'f5e8beaf989d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

alert_resolution = sa.Enum("confirmed_fraud", "false_positive", name="alert_resolution")


def upgrade() -> None:
    # 1. Créer le type ENUM côté PostgreSQL (checkfirst : idempotent).
    alert_resolution.create(op.get_bind(), checkfirst=True)
    # 2. Puis seulement ajouter la colonne qui l'utilise.
    op.add_column("alerts", sa.Column("resolution", alert_resolution, nullable=True))


def downgrade() -> None:
    op.drop_column("alerts", "resolution")
    alert_resolution.drop(op.get_bind(), checkfirst=True)
