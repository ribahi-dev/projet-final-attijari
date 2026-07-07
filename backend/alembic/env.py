"""Configuration d'exécution d'Alembic — le "git de la base de données".

Pourquoi Alembic : create_all() crée les tables manquantes mais ne sait
PAS modifier une table existante (ajouter une colonne, changer un type).
Alembic versionne chaque évolution du schéma dans un fichier de migration
(upgrade/downgrade) : la base de chaque membre du trinôme, de la CI et de
la démo avance par les mêmes étapes, dans le même ordre, rejouables.

Deux branchements faits ici par rapport au fichier généré par défaut :
  1. l'URL de connexion vient de app.core.config (donc du .env) — jamais
     en dur dans alembic.ini ;
  2. target_metadata = Base.metadata pour que `--autogenerate` compare
     les modèles SQLAlchemy à la base réelle et écrive la migration seul.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app import models  # noqa: F401  (charge tous les modèles dans Base.metadata)
from app.core.config import settings
from app.db.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Mode offline : génère le SQL sans se connecter (utile pour revue DBA)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Mode online : applique les migrations sur la base connectée."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
