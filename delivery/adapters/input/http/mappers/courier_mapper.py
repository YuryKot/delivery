from delivery.adapters.input.http.models.courier import Courier as HttpCourier
from delivery.adapters.input.http.models.courier import CreateCourierResponse
from delivery.adapters.input.http.models.location import Location as HttpLocation
from delivery.core.application.queries.get_all_couriers.dto import CourierDto


class CourierMapper:
    @staticmethod
    def to_http(dto: CourierDto) -> HttpCourier:
        return HttpCourier(
            id=dto.id,
            name=dto.name,
            location=HttpLocation(x=dto.location_x, y=dto.location_y).model_dump(),
        )

    @staticmethod
    def to_http_create_response(courier_id: str) -> CreateCourierResponse:
        return CreateCourierResponse(courierId=courier_id)
