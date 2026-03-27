from abc import ABC, abstractmethod

from delivery.core.domain.model.kernel import Location
from delivery.libs.errs.error import Error
from delivery.libs.errs.result import Result


class GeoLocationClient(ABC):
    @abstractmethod
    async def get_location(self, street: str) -> Result[Location, Error]: ...
