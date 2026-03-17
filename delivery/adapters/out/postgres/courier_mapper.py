import typing

from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.courier.storage_place import StoragePlace
from delivery.core.domain.model.kernel import Location
from delivery.database.models import CourierModel, StoragePlaceModel


def _storage_place_to_domain(model: StoragePlaceModel) -> StoragePlace:
    return StoragePlace(
        id_=model.id,
        name=model.name,
        total_volume=model.total_volume,
        order_id=model.order_id,
    )


def _storage_place_to_model(place: StoragePlace, courier_id: object) -> StoragePlaceModel:
    return StoragePlaceModel(
        id=place.id,
        courier_id=courier_id,
        name=place.name,
        total_volume=place.total_volume,
        order_id=place.order_id,
    )


def to_domain(model: CourierModel) -> Courier:
    location: typing.Final[Location] = Location.must_create(model.location_x, model.location_y)
    storage_places: typing.Final[list[StoragePlace]] = [_storage_place_to_domain(sp) for sp in model.storage_places]
    return Courier(
        id_=model.id,
        name=model.name,
        speed=model.speed,
        location=location,
        storage_places=storage_places,
    )


def to_model(courier: Courier) -> CourierModel:
    courier_model: typing.Final[CourierModel] = CourierModel(
        id=courier.id,
        name=courier.name,
        speed=courier.speed,
        location_x=courier.location.x,
        location_y=courier.location.y,
    )
    courier_model.storage_places = [_storage_place_to_model(place, courier.id) for place in courier.storage_places]
    return courier_model
