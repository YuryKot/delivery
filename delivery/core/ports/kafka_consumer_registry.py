import typing

from delivery.core.ports.kafka_consumer import KafkaConsumer


class KafkaConsumerRegistry:
    _consumers: typing.ClassVar[dict[type[KafkaConsumer], str]] = {}

    @classmethod
    def register(
        cls,
        consumer_class: type[KafkaConsumer],
        topic: str | None = None,
        group_id: str | None = None,
    ) -> type[KafkaConsumer]:
        cls._consumers[consumer_class] = f"{topic or ''}:{group_id or ''}"
        return consumer_class

    @classmethod
    def get_all_consumers(cls) -> list[type[KafkaConsumer]]:
        return list(cls._consumers.keys())
