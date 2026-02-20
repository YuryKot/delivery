import asyncio
import typing
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from delivery.database.models import BaseServiceModel
from delivery.settings import settings

target_metadata: typing.Final = BaseServiceModel.metadata
main_alembic_config: typing.Final = context.config

if main_alembic_config.config_file_name is not None:
    fileConfig(main_alembic_config.config_file_name)


def run_migrations_offline() -> None:
    context.configure(
        url=settings.main_database_dsn,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    alembic_configs: typing.Final[dict[str, str]] = main_alembic_config.get_section(
        main_alembic_config.config_ini_section,
        {},
    )
    alembic_configs["sqlalchemy.url"] = settings.main_database_dsn.render_as_string(hide_password=False)

    connectable: typing.Final = async_engine_from_config(
        alembic_configs,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
