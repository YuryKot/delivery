import typing

import pytest
from fastapi.testclient import TestClient
import sqlalchemy.ext.asyncio as sa_async

from delivery.application import build_app
from delivery.ioc import IOCContainer


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
async def _clear_ioc_container() -> typing.AsyncIterator[None]:
    yield
    IOCContainer.reset_override_sync()
    await IOCContainer.tear_down()


@pytest.fixture(scope="session", autouse=True)
async def db_connection() -> typing.AsyncIterator[sa_async.AsyncConnection]:
    engine: typing.Final = await IOCContainer.main_database_engine()
    connection: typing.Final = await engine.connect()
    yield connection
    await connection.close()


@pytest.fixture(autouse=True)
async def _rollback_database(db_connection: sa_async.AsyncConnection) -> typing.AsyncIterator[None]:
    transaction: typing.Final = await db_connection.begin()
    await db_connection.begin_nested()
    session: typing.Final = sa_async.AsyncSession(db_connection, expire_on_commit=False)
    IOCContainer.main_database_session.override_sync(session)
    IOCContainer.replica_database_session.override_sync(session)

    yield
    if db_connection.in_transaction():
        await transaction.rollback()
    await db_connection.close()


@pytest.fixture()
def test_client() -> typing.Iterator[TestClient]:
    with TestClient(app=build_app()) as app_client:
        yield app_client
