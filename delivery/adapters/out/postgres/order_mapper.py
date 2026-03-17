import typing

from delivery.core.domain.model.kernel import Location
from delivery.core.domain.model.order.order import Order
from delivery.core.domain.model.order.order_status import OrderStatus
from delivery.database.models import OrderModel


def to_domain(model: OrderModel) -> Order:
    location: typing.Final[Location] = Location.must_create(model.location_x, model.location_y)
    return Order(
        id_=model.id,
        location=location,
        volume=model.volume,
        status=OrderStatus(model.status),
        courier_id=model.courier_id,
    )


def to_model(order: Order) -> OrderModel:
    return OrderModel(
        id=order.id,
        location_x=order.location.x,
        location_y=order.location.y,
        volume=order.volume,
        status=order.status.value,
        courier_id=order.courier_id,
    )
