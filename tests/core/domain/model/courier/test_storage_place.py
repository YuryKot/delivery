import typing
from uuid import UUID, uuid4

import pytest

from delivery.core.domain.model.courier.storage_place import StoragePlace
from delivery.libs.errs.error import DomainInvariantError


class TestStoragePlaceCreation:
    @pytest.mark.parametrize(
        ("name", "total_volume", "order_id"),
        [
            ("Рюкзак", 100, None),
            ("Багажник", 500, None),
            ("Сумка", 50, None),
            ("Рюкзак", 100, uuid4()),
            ("Багажник", 1, None),
            ("Сумка", 1000, None),
        ],
        ids=[
            "backpack_empty",
            "trunk_empty",
            "bag_empty",
            "backpack_with_order",
            "min_volume",
            "large_volume",
        ],
    )
    def test_create_valid_storage_place(
        self,
        name: str,
        total_volume: int,
        order_id: UUID | None,
    ) -> None:
        result: typing.Final = StoragePlace.create(name, total_volume, order_id)

        assert result.is_success
        storage: typing.Final = result.get_value()
        assert storage.id is not None
        assert storage.name == name
        assert storage.total_volume == total_volume
        assert storage.order_id == order_id

    @pytest.mark.parametrize(
        ("name", "total_volume", "error_code_fragment"),
        [
            ("", 100, "value.is.required"),
            ("Рюкзак", 0, "must.be.greater.or.equal"),
            ("Багажник", -10, "must.be.greater.or.equal"),
        ],
        ids=[
            "empty_name",
            "zero_volume",
            "negative_volume",
        ],
    )
    def test_create_invalid_storage_place(
        self,
        name: str,
        total_volume: int,
        error_code_fragment: str,
    ) -> None:
        result: typing.Final = StoragePlace.create(name, total_volume)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert error_code_fragment in error.code

    @pytest.mark.parametrize(
        ("name", "total_volume"),
        [
            ("Рюкзак", 100),
            ("Багажник", 500),
        ],
    )
    def test_must_create_valid_storage_place(self, name: str, total_volume: int) -> None:
        storage: typing.Final = StoragePlace.must_create(name, total_volume)

        assert storage.id is not None
        assert storage.name == name
        assert storage.total_volume == total_volume

    @pytest.mark.parametrize(
        ("name", "total_volume"),
        [
            ("", 100),
            ("Рюкзак", 0),
            ("Багажник", -5),
        ],
    )
    def test_must_create_invalid_storage_place_raises_exception(
        self,
        name: str,
        total_volume: int,
    ) -> None:
        with pytest.raises(DomainInvariantError):
            StoragePlace.must_create(name, total_volume)


class TestStoragePlaceEquality:
    def test_different_id_different_entity(self) -> None:
        storage1: typing.Final = StoragePlace.must_create("Рюкзак", 100)
        storage2: typing.Final = StoragePlace.must_create("Рюкзак", 100)

        assert storage1 != storage2
        assert storage2 != storage1


class TestStoragePlaceIsOccupied:
    def test_storage_without_order_is_not_occupied(self) -> None:
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100)

        assert not storage.is_occupied()

    def test_storage_with_order_is_occupied(self) -> None:
        order_id: typing.Final = uuid4()
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100, order_id)

        assert storage.is_occupied()


class TestStoragePlaceCanPlaceOrder:
    @pytest.mark.parametrize(
        ("total_volume", "order_volume", "can_place"),
        [
            (100, 50, True),
            (100, 100, True),
            (100, 99, True),
            (100, 101, False),
            (100, 200, False),
            (50, 1, True),
            (1, 1, True),
        ],
        ids=[
            "half_volume",
            "exact_volume",
            "almost_full",
            "slightly_exceeds",
            "double_volume",
            "minimal_order",
            "exact_minimal",
        ],
    )
    def test_can_place_order_in_empty_storage(
        self,
        total_volume: int,
        order_volume: int,
        can_place: bool,
    ) -> None:
        storage: typing.Final = StoragePlace.must_create("Рюкзак", total_volume)

        assert storage.can_store(order_volume) == can_place

    def test_cannot_place_order_in_occupied_storage(self) -> None:
        existing_order: typing.Final = uuid4()
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100, existing_order)

        assert not storage.can_store(50)
        assert not storage.can_store(100)


class TestStoragePlacePlaceOrder:
    @pytest.mark.parametrize(
        ("total_volume", "order_volume"),
        [
            (100, 50),
            (100, 100),
            (100, 1),
            (500, 499),
        ],
        ids=[
            "half_volume",
            "exact_volume",
            "minimal_volume",
            "almost_full",
        ],
    )
    def test_place_order_success(self, total_volume: int, order_volume: int) -> None:
        storage: typing.Final = StoragePlace.must_create("Рюкзак", total_volume)
        order_id: typing.Final = uuid4()

        result: typing.Final = storage.store(order_id, order_volume)

        assert result.is_success
        assert storage.order_id == order_id
        assert storage.is_occupied()

    def test_place_order_volume_exceeds(self) -> None:
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100)
        order_id: typing.Final = uuid4()

        result: typing.Final = storage.store(order_id, 150)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "storage.place.volume.exceeded" in error.code
        assert not storage.is_occupied()

    def test_place_order_already_occupied(self) -> None:
        existing_order: typing.Final = uuid4()
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100, existing_order)
        new_order: typing.Final = uuid4()

        result: typing.Final = storage.store(new_order, 50)

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "storage.place.already.occupied" in error.code
        assert storage.order_id == existing_order


class TestStoragePlaceRemoveOrder:
    def test_remove_order_success(self) -> None:
        order_id: typing.Final = uuid4()
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100, order_id)

        result: typing.Final = storage.clear()

        assert result.is_success
        assert not storage.is_occupied()
        assert storage.order_id is None

    def test_remove_order_from_empty_storage(self) -> None:
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100)

        result: typing.Final = storage.clear()

        assert result.is_failure
        error: typing.Final = result.get_error()
        assert "storage.place.already.empty" in error.code


class TestStoragePlaceWorkflow:
    def test_place_and_remove_order_workflow(self) -> None:
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100)
        order_id: typing.Final = uuid4()

        assert not storage.is_occupied()
        assert storage.can_store(80)

        place_result: typing.Final = storage.store(order_id, 80)
        assert place_result.is_success
        assert storage.is_occupied()
        assert storage.order_id == order_id
        assert not storage.can_store(20)

        remove_result: typing.Final = storage.clear()
        assert remove_result.is_success
        assert not storage.is_occupied()
        assert storage.can_store(80)

    def test_cannot_place_two_orders_sequentially(self) -> None:
        storage: typing.Final = StoragePlace.must_create("Рюкзак", 100)
        first_order: typing.Final = uuid4()
        second_order: typing.Final = uuid4()

        first_result: typing.Final = storage.store(first_order, 50)
        assert first_result.is_success

        second_result: typing.Final = storage.store(second_order, 30)
        assert second_result.is_failure
        assert storage.order_id == first_order
