import typing

import psycopg
import sqlalchemy.ext.asyncio as sa_async
import that_depends
from db_utils.retries import make_async_retry_session_class
from that_depends import ContextScopes, providers

from delivery.adapters.out.postgres.courier_repository import CourierRepositoryImpl
from delivery.adapters.out.postgres.order_repository import OrderRepositoryImpl
from delivery.adapters.out.postgres.unit_of_work import UnitOfWorkImpl
from delivery.core.domain.service.order_dispatch_service import OrderDispatchDomainService
from delivery.settings import settings


async def create_database_engine() -> typing.AsyncIterator[sa_async.AsyncEngine]:
    engine: typing.Final = sa_async.create_async_engine(url=settings.database_dsn)
    try:
        yield engine
    finally:
        await engine.dispose()


async def create_database_session(database_engine: sa_async.AsyncEngine) -> typing.AsyncIterator[sa_async.AsyncSession]:
    retry_class: typing.Final = make_async_retry_session_class(
        exception_types=[psycopg.DatabaseError], retries=settings.database_connection_retries
    )
    async with retry_class(database_engine, expire_on_commit=False) as session:
        yield session


class IOCContainer(that_depends.BaseContainer):
    default_scope = ContextScopes.REQUEST

    main_database_engine = providers.Resource(create_database_engine)
    main_database_session = providers.ContextResource(create_database_session, main_database_engine.cast)
    replica_database_engine = providers.Resource(create_database_engine)
    replica_database_session = providers.ContextResource(create_database_session, replica_database_engine.cast)

    order_dispatch_service = providers.Factory(OrderDispatchDomainService)

    order_repository = providers.Factory(OrderRepositoryImpl, main_database_session.cast)
    courier_repository = providers.Factory(CourierRepositoryImpl, main_database_session.cast)
    unit_of_work = providers.Factory(UnitOfWorkImpl, main_database_session.cast)
