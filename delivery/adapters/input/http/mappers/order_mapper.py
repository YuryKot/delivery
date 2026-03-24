from delivery.adapters.input.http.models.location import Location as HttpLocation
from delivery.adapters.input.http.models.order import CreateOrderResponse
from delivery.adapters.input.http.models.order import Order as HttpOrder
from delivery.core.application.queries.get_all_incomplete_orders.dto import IncompleteOrderDto


class OrderMapper:
    @staticmethod
    def to_http(dto: IncompleteOrderDto) -> HttpOrder:
        return HttpOrder(
            id=dto.id,
            location=HttpLocation(x=dto.location_x, y=dto.location_y).model_dump(),
        )

    @staticmethod
    def to_http_create_response(order_id: str) -> CreateOrderResponse:
        return CreateOrderResponse(orderId=order_id)
