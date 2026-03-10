import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

# load Flask app config
flask_app = create_app()

config = context.config
fileConfig(config.config_file_name)

# override sqlalchemy.url with Flasks app's dtabase URL
db_url = flask_app.config.get("DATABASE_URL", "devstack.db")
if not db_url.startswith("sqlite:///"):
    db_url = f"sqlite:///{db_url}"
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline():
    """Run migrations witout a live db connection"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # required for SQLite
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Runs migrations with a livev db connection"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            render_as_batch=True,  # required for SQLite
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
