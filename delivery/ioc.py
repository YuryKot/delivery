import typing

import psycopg
import sqlalchemy.ext.asyncio as sa_async
import that_depends
from db_utils.retries import make_async_retry_session_class
from that_depends import ContextScopes, providers

from delivery.adapters.input.kafka.basket_events_consumer import BasketEventsConsumer
from delivery.adapters.out.grps.geo_client_impl import GeoClientImpl
from delivery.adapters.out.postgres.courier_repository import CourierRepositoryImpl
from delivery.adapters.out.postgres.order_repository import OrderRepositoryImpl
from delivery.core.application.commands.assign_order_to_courier import AssignOrderToCourierCommandHandlerImpl
from delivery.core.application.commands.create_courier import CreateCourierCommandHandlerImpl
from delivery.core.application.commands.create_order import CreateOrderCommandHandlerImpl
from delivery.core.application.commands.move_couriers import MoveCouriersCommandHandlerImpl
from delivery.core.application.queries.get_all_couriers import GetAllCouriersQueryHandlerImpl
from delivery.core.application.queries.get_all_incomplete_orders import GetAllIncompleteOrdersQueryHandlerImpl
from delivery.core.application.services.kafka_consumer_resolver import KafkaConsumerResolver
from delivery.core.domain.service.order_dispatch_service import OrderDispatchDomainService
from delivery.event_publisher import DefaultDomainEventPublisher
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

    geo_location_client = providers.Factory(
        GeoClientImpl,
        settings.geo_service_grpc_host,
        settings.geo_service_grpc_port,
    )
    order_repository = providers.Factory(OrderRepositoryImpl, main_database_session.cast)
    courier_repository = providers.Factory(CourierRepositoryImpl, main_database_session.cast)

    domain_event_publisher = providers.Singleton(DefaultDomainEventPublisher)
    create_courier_handler = providers.Factory(
        CreateCourierCommandHandlerImpl, courier_repository.cast, domain_event_publisher.cast
    )
    create_order_handler = providers.Factory(
        CreateOrderCommandHandlerImpl,
        order_repository.cast,
        courier_repository.cast,
        geo_location_client.cast,
        domain_event_publisher.cast,
    )
    move_couriers_handler = providers.Factory(
        MoveCouriersCommandHandlerImpl,
        domain_event_publisher.cast,
    )
    assign_order_to_courier_handler = providers.Factory(
        AssignOrderToCourierCommandHandlerImpl,
        order_dispatch_service.cast,
        domain_event_publisher.cast,
    )
    get_all_couriers_handler = providers.Factory(
        GetAllCouriersQueryHandlerImpl,
        main_database_session.cast,
    )
    get_all_incomplete_orders_handler = providers.Factory(
        GetAllIncompleteOrdersQueryHandlerImpl,
        main_database_session.cast,
    )

    app_main_database_session = providers.Resource(create_database_session, main_database_engine.cast)
    app_order_repository = providers.Factory(OrderRepositoryImpl, app_main_database_session.cast)
    app_courier_repository = providers.Factory(CourierRepositoryImpl, app_main_database_session.cast)
    app_order_dispatch_service = providers.Factory(OrderDispatchDomainService)
    app_domain_event_publisher = providers.Singleton(DefaultDomainEventPublisher)

    app_assign_order_to_courier_handler = providers.Factory(
        AssignOrderToCourierCommandHandlerImpl,
        app_order_dispatch_service.cast,
        app_domain_event_publisher.cast,
    )
    app_move_couriers_handler = providers.Factory(
        MoveCouriersCommandHandlerImpl,
        app_domain_event_publisher.cast,
    )

    # Kafka consumers
    basket_events_consumer = providers.Factory(
        BasketEventsConsumer,
        create_order_handler.cast,
    )
    kafka_consumer_resolver = providers.Factory(
        KafkaConsumerResolver,
        basket_events_consumer.cast,
    )
