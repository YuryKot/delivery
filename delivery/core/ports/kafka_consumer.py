from abc import ABC, abstractmethod


class KafkaConsumer(ABC):
    @property
    @abstractmethod
    def topic(self) -> str:
        pass

    @property
    @abstractmethod
    def group_id(self) -> str | None:
        pass

    @abstractmethod
    async def consume(self, message: bytes) -> None:
        pass
