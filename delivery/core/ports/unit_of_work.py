import contextlib
import dataclasses
import typing

import psycopg
from db_utils.retries import make_async_retry_session_class

from delivery.core.ports.courier_repository import CourierRepository
from delivery.core.ports.order_repository import OrderRepository
from delivery.core.ports.outbox_repository import OutboxRepository
from delivery.libs.ddd import DomainEventPublisher
from delivery.settings import settings


@dataclasses.dataclass(frozen=True, kw_only=True, slots=True)
class DeliveryUnitOfWork:
    order: OrderRepository
    courier: CourierRepository
    outbox: OutboxRepository
    domain_event_publisher: DomainEventPublisher

    @classmethod
    @contextlib.asynccontextmanager
    async def start(cls) -> typing.AsyncIterator[typing.Self]:

        from delivery.adapters.out.postgres.courier_repository import CourierRepositoryImpl  # noqa: PLC0415
        from delivery.adapters.out.postgres.order_repository import OrderRepositoryImpl  # noqa: PLC0415
        from delivery.adapters.out.postgres.outbox_domain_event_publisher import (  # noqa: PLC0415
            OutboxDomainEventPublisher,
        )
        from delivery.adapters.out.postgres.outbox_repository import OutboxRepositoryImpl  # noqa: PLC0415
        from delivery.ioc import IOCContainer  # noqa: PLC0415

        engine: typing.Final = await IOCContainer.main_database_engine()

        retry_class: typing.Final = make_async_retry_session_class(
            exception_types=[psycopg.DatabaseError],
            retries=settings.database_connection_retries,
        )

        async with retry_class(engine, expire_on_commit=False) as session:
            try:
                order_repo: typing.Final = OrderRepositoryImpl(session=session)
                courier_repo: typing.Final = CourierRepositoryImpl(session=session)
                outbox_repo: typing.Final = OutboxRepositoryImpl(session=session)
                publisher: typing.Final = OutboxDomainEventPublisher(outbox_repo)

                yield cls(
                    order=order_repo,
                    courier=courier_repo,
                    outbox=outbox_repo,
                    domain_event_publisher=publisher,
                )
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()
