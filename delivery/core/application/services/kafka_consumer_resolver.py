from delivery.core.ports.kafka_consumer import KafkaConsumer


class KafkaConsumerResolver:
    def __init__(
        self,
        basket_events_consumer: KafkaConsumer,
    ) -> None:
        self._consumers: dict[type[KafkaConsumer], KafkaConsumer] = {
            self._get_consumer_class_from_instance(basket_events_consumer): basket_events_consumer,
        }

    def _get_consumer_class_from_instance(self, instance: KafkaConsumer) -> type[KafkaConsumer]:
        return type(instance)

    def get_consumer(self, consumer_class: type[KafkaConsumer]) -> KafkaConsumer:
        if consumer_class not in self._consumers:
            raise ValueError(f"Unknown consumer class: {consumer_class}")
        return self._consumers[consumer_class]
