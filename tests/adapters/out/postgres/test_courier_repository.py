import typing
import uuid

import pytest
import sqlalchemy.ext.asyncio as sa_async

from delivery.adapters.out.postgres.courier_repository import CourierRepositoryImpl
from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.kernel import Location, Volume
from delivery.core.domain.model.order.order import Order
from delivery.core.ports.courier_repository import CourierRepository


@pytest.fixture
async def courier_repository(db_connection: sa_async.AsyncConnection) -> CourierRepository:
    session: typing.Final = sa_async.AsyncSession(db_connection, expire_on_commit=False)
    return CourierRepositoryImpl(session)


@pytest.mark.usefixtures("_rollback_database")
class TestCourierRepository:
    @staticmethod
    def _create_courier(
        name: str,
        speed: int,
        location_x: int,
        location_y: int,
    ) -> Courier:
        location: typing.Final = Location.must_create(location_x, location_y)
        return Courier.must_create(name=name, speed=speed, location=location)

    @staticmethod
    def _create_order(location: Location, volume: int) -> Order:
        order_id: typing.Final = uuid.uuid4()
        return Order.must_create(id_=order_id, location=location, volume=Volume.must_create(volume))

    async def test_add_and_get_by_id(
        self,
        courier_repository: CourierRepository,
    ) -> None:
        courier: typing.Final = self._create_courier(
            name="Test Courier",
            speed=10,
            location_x=5,
            location_y=5,
        )

        await courier_repository.add(courier)
        retrieved: typing.Final = await courier_repository.get_by_id(courier.id)  # type: ignore[arg-type]

        assert retrieved is not None
        assert retrieved.id == courier.id
        assert retrieved.name == courier.name
        assert retrieved.speed == courier.speed
        assert retrieved.location.x == courier.location.x
        assert retrieved.location.y == courier.location.y
        assert len(retrieved.storage_places) == len(courier.storage_places)

    async def test_get_by_id_not_found(
        self,
        courier_repository: CourierRepository,
    ) -> None:
        non_existent_id: typing.Final = uuid.uuid4()
        result: typing.Final = await courier_repository.get_by_id(non_existent_id)
        assert result is None

    async def test_update_courier(
        self,
        courier_repository: CourierRepository,
    ) -> None:
        courier: typing.Final = self._create_courier(
            name="Original Name",
            speed=10,
            location_x=1,
            location_y=1,
        )

        await courier_repository.add(courier)

        courier._name = "Updated Name"  # noqa: SLF001
        courier._speed = 20  # noqa: SLF001
        courier._location = Location.must_create(10, 10)  # noqa: SLF001

        await courier_repository.update(courier)
        retrieved: typing.Final = await courier_repository.get_by_id(courier.id)  # type: ignore[arg-type]

        assert retrieved is not None
        assert retrieved.name == "Updated Name"
        assert retrieved.speed == 20
        assert retrieved.location.x == 10
        assert retrieved.location.y == 10

    async def test_update_courier_storage_places(
        self,
        courier_repository: CourierRepository,
    ) -> None:
        courier: typing.Final = self._create_courier(
            name="Storage Test",
            speed=10,
            location_x=1,
            location_y=1,
        )

        await courier_repository.add(courier)

        extra_storage: typing.Final = courier.storage_places[0]
        extra_storage._name = "Updated Storage"  # noqa: SLF001
        extra_storage._total_volume = 20  # noqa: SLF001

        await courier_repository.update(courier)
        retrieved: typing.Final = await courier_repository.get_by_id(courier.id)  # type: ignore[arg-type]

        assert retrieved is not None
        assert len(retrieved.storage_places) == 1
        assert retrieved.storage_places[0].name == "Updated Storage"
        assert retrieved.storage_places[0].total_volume == 20

    async def test_get_all_free_with_no_orders(
        self,
        courier_repository: CourierRepository,
    ) -> None:
        courier1: typing.Final = self._create_courier(
            name="Free Courier 1",
            speed=10,
            location_x=1,
            location_y=1,
        )
        courier2: typing.Final = self._create_courier(
            name="Free Courier 2",
            speed=15,
            location_x=5,
            location_y=5,
        )

        await courier_repository.add(courier1)
        await courier_repository.add(courier2)

        free_couriers: typing.Final = await courier_repository.get_all_free()

        assert len(free_couriers) == 2
        courier_ids: typing.Final = {c.id for c in free_couriers}
        assert courier1.id in courier_ids
        assert courier2.id in courier_ids

    async def test_get_all_free_excludes_occupied_couriers(
        self,
        courier_repository: CourierRepository,
    ) -> None:
        free_courier: typing.Final = self._create_courier(
            name="Free Courier",
            speed=10,
            location_x=1,
            location_y=1,
        )
        occupied_courier: typing.Final = self._create_courier(
            name="Occupied Courier",
            speed=10,
            location_x=5,
            location_y=5,
        )

        await courier_repository.add(free_courier)
        await courier_repository.add(occupied_courier)

        order: typing.Final = self._create_order(
            location=Location.must_create(5, 5),
            volume=5,
        )
        take_result: typing.Final = occupied_courier.take_order(order.id, Volume.must_create(5))  # type: ignore[arg-type]
        assert take_result.is_success

        await courier_repository.update(occupied_courier)

        free_couriers: typing.Final = await courier_repository.get_all_free()

        assert len(free_couriers) == 1
        assert free_couriers[0].id == free_courier.id
        assert free_couriers[0].name == "Free Courier"

    async def test_get_all_free_with_multiple_storage_places(
        self,
        courier_repository: CourierRepository,
    ) -> None:
        courier: typing.Final = self._create_courier(
            name="Multi Storage Courier",
            speed=10,
            location_x=3,
            location_y=3,
        )

        add_result: typing.Final = courier.add_storage_place("Extra Bag", 15)
        assert add_result.is_success

        await courier_repository.add(courier)

        free_couriers: typing.Final = await courier_repository.get_all_free()

        assert len(free_couriers) == 1
        retrieved: typing.Final = free_couriers[0]
        assert retrieved.id == courier.id
        assert len(retrieved.storage_places) == 2
