from uuid import UUID

from delivery.core.domain.model.kernel import Address, Volume


class CreateOrderCommand:
    def __init__(
        self,
        order_id: UUID,
        address: Address,
        volume: Volume,
    ) -> None:
        self._order_id = order_id
        self._address = address
        self._volume = volume

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def address(self) -> Address:
        return self._address

    @property
    def volume(self) -> Volume:
        return self._volume
