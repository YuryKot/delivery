import typing
from uuid import UUID, uuid4

from delivery.core.domain.model.courier.courier import Courier
from delivery.core.domain.model.kernel import Location, Volume
from delivery.core.domain.model.order.order import Order


def create_test_courier(
    name: str = "Test Courier",
    speed: int = 10,
    location: Location | None = None,
) -> Courier:
    return Courier.must_create(
        name=name,
        speed=speed,
        location=location or Location.must_create(1, 1),
    )


def create_test_order(
    order_id: UUID | None = None,
    location: Location | None = None,
    volume: int = 1,
    courier_id: UUID | None = None,
) -> Order:
    order: typing.Final = Order.must_create(
        id_=order_id or uuid4(),
        location=location or Location.must_create(5, 5),
        volume=Volume.must_create(volume),
    )
    if courier_id is not None:
        order.assign(courier_id)
    return order
