from uuid import UUID


class CreateOrderCommand:
    def __init__(  # noqa: PLR0913
        self,
        order_id: UUID,
        country: str,
        city: str,
        street: str,
        house: str,
        apartment: str,
        volume: int,
    ) -> None:
        self._order_id = order_id
        self._country = country
        self._city = city
        self._street = street
        self._house = house
        self._apartment = apartment
        self._volume = volume

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def country(self) -> str:
        return self._country

    @property
    def city(self) -> str:
        return self._city

    @property
    def street(self) -> str:
        return self._street

    @property
    def house(self) -> str:
        return self._house

    @property
    def apartment(self) -> str:
        return self._apartment

    @property
    def volume(self) -> int:
        return self._volume
