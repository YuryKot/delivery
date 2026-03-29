import typing
from uuid import UUID

from delivery.adapters.input.kafka import baskets_events_pb2 as pb2
from delivery.core.application.commands.create_order.command import CreateOrderCommand
from delivery.core.domain.model.kernel import Address, Volume
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result


def map_basket_confirmed_to_create_order_command(
    event: pb2.BasketConfirmedIntegrationEvent,
) -> Result[CreateOrderCommand, Error]:
    try:
        order_id: typing.Final = UUID(event.basket_id)

        address_result: typing.Final = Address.create(
            country=event.address.country,
            city=event.address.city,
            street=event.address.street,
            house=event.address.house,
            apartment=event.address.apartment,
        )
        if address_result.is_failure:
            return Result.failure(address_result.get_error())

        volume_result: typing.Final = Volume.create(event.volume)
        if volume_result.is_failure:
            return Result.failure(volume_result.get_error())

        command: typing.Final = CreateOrderCommand(
            order_id=order_id,
            address=address_result.get_value(),
            volume=volume_result.get_value(),
        )
        return Result.success(command)

    except ValueError as e:
        return Result.failure(
            Error.of(
                "basket.event.invalid.uuid",
                f"Invalid UUID in basket event: {e!s}",
            )
        )
    except AttributeError as e:
        return Result.failure(
            Error.of(
                "basket.event.missing.field",
                f"Missing required field in basket event: {e!s}",
            )
        )
