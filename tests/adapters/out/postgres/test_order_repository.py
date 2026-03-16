import typing
import uuid

import pytest
import sqlalchemy.ext.asyncio as sa_async

from delivery.adapters.out.postgres.order_repository import OrderRepositoryImpl
from delivery.core.domain.model.kernel import Location
from delivery.core.domain.model.order.order import Order
from delivery.core.domain.model.order.order_status import OrderStatus
from delivery.core.ports.order_repository import OrderRepository


@pytest.fixture
async def order_repository(db_connection: sa_async.AsyncConnection) -> OrderRepository:
    session: typing.Final = sa_async.AsyncSession(db_connection, expire_on_commit=False)
    return OrderRepositoryImpl(session)


@pytest.mark.usefixtures("_rollback_database")
class TestOrderRepository:
    @staticmethod
    def _create_order(location: Location, volume: int) -> Order:
        order_id: typing.Final = uuid.uuid4()
        return Order.must_create(id_=order_id, location=location, volume=volume)

    async def test_add_and_get_by_id(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = self._create_order(location=location, volume=10)

        await order_repository.add(order)
        retrieved: typing.Final = await order_repository.get_by_id(order.id)  # type: ignore[arg-type]

        assert retrieved is not None
        assert retrieved.id == order.id
        assert retrieved.location.x == order.location.x
        assert retrieved.location.y == order.location.y
        assert retrieved.volume == order.volume
        assert retrieved.status == order.status
        assert retrieved.courier_id is None

    async def test_get_by_id_not_found(
        self,
        order_repository: OrderRepository,
    ) -> None:
        non_existent_id: typing.Final = uuid.uuid4()
        result: typing.Final = await order_repository.get_by_id(non_existent_id)
        assert result is None

    async def test_update_order(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = self._create_order(location=location, volume=10)

        await order_repository.add(order)

        courier_id: typing.Final = uuid.uuid4()
        assign_result: typing.Final = order.assign(courier_id)
        assert assign_result.is_success

        await order_repository.update(order)
        retrieved: typing.Final = await order_repository.get_by_id(order.id)  # type: ignore[arg-type]

        assert retrieved is not None
        assert retrieved.status == OrderStatus.ASSIGNED
        assert retrieved.courier_id == courier_id

    async def test_get_first_by_status_created(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        order1: typing.Final = self._create_order(location=location, volume=10)
        order2: typing.Final = self._create_order(location=location, volume=15)

        await order_repository.add(order1)
        await order_repository.add(order2)

        retrieved: typing.Final = await order_repository.get_first_by_status_created()

        assert retrieved is not None
        assert retrieved.status == OrderStatus.CREATED
        assert retrieved.id == order1.id

    async def test_get_first_by_status_created_returns_first(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        order1: typing.Final = self._create_order(location=location, volume=10)
        order2: typing.Final = self._create_order(location=location, volume=15)

        await order_repository.add(order1)
        await order_repository.add(order2)

        retrieved: typing.Final = await order_repository.get_first_by_status_created()

        assert retrieved is not None
        assert retrieved.id == order1.id

    async def test_get_first_by_status_created_no_matches(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = self._create_order(location=location, volume=10)

        courier_id: typing.Final = uuid.uuid4()
        assign_result: typing.Final = order.assign(courier_id)
        assert assign_result.is_success

        await order_repository.add(order)

        retrieved: typing.Final = await order_repository.get_first_by_status_created()

        assert retrieved is None

    async def test_get_all_assigned(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        order1: typing.Final = self._create_order(location=location, volume=10)
        order2: typing.Final = self._create_order(location=location, volume=15)

        await order_repository.add(order1)
        await order_repository.add(order2)

        courier_id: typing.Final = uuid.uuid4()
        assign_result1: typing.Final = order1.assign(courier_id)
        assign_result2: typing.Final = order2.assign(courier_id)
        assert assign_result1.is_success
        assert assign_result2.is_success

        await order_repository.update(order1)
        await order_repository.update(order2)

        assigned_orders: typing.Final = await order_repository.get_all_assigned()

        assert len(assigned_orders) == 2
        order_ids: typing.Final = {o.id for o in assigned_orders}
        assert order1.id in order_ids
        assert order2.id in order_ids
        assert all(o.status == OrderStatus.ASSIGNED for o in assigned_orders)

    async def test_get_all_assigned_empty(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = self._create_order(location=location, volume=10)

        await order_repository.add(order)

        assigned_orders: typing.Final = await order_repository.get_all_assigned()

        assert len(assigned_orders) == 0

    async def test_get_all_assigned_excludes_created_orders(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        created_order: typing.Final = self._create_order(location=location, volume=10)
        assigned_order: typing.Final = self._create_order(location=location, volume=15)

        await order_repository.add(created_order)
        await order_repository.add(assigned_order)

        courier_id: typing.Final = uuid.uuid4()
        assign_result: typing.Final = assigned_order.assign(courier_id)
        assert assign_result.is_success

        await order_repository.update(assigned_order)

        assigned_orders: typing.Final = await order_repository.get_all_assigned()

        assert len(assigned_orders) == 1
        assert assigned_orders[0].id == assigned_order.id
        assert assigned_orders[0].status == OrderStatus.ASSIGNED

    async def test_update_order_complete(
        self,
        order_repository: OrderRepository,
    ) -> None:
        location: typing.Final = Location.must_create(5, 5)
        order: typing.Final = self._create_order(location=location, volume=10)

        await order_repository.add(order)

        courier_id: typing.Final = uuid.uuid4()
        assign_result: typing.Final = order.assign(courier_id)
        assert assign_result.is_success

        complete_result: typing.Final = order.complete()
        assert complete_result.is_success

        await order_repository.update(order)
        retrieved: typing.Final = await order_repository.get_by_id(order.id)  # type: ignore[arg-type]

        assert retrieved is not None
        assert retrieved.status == OrderStatus.COMPLETED
        assert retrieved.courier_id == courier_id
