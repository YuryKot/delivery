import typing

from fastapi import FastAPI
from faststream.kafka import KafkaBroker

from delivery.core.ports.kafka_consumer import KafkaConsumer
from delivery.core.ports.kafka_consumer_registry import KafkaConsumerRegistry
from delivery.settings import settings


def create_kafka_broker() -> KafkaBroker:
    broker: typing.Final = KafkaBroker(
        settings.kafka_bootstrap_servers,
    )
    return broker


def setup_kafka_broker(app: FastAPI, broker: KafkaBroker) -> None:
    from delivery.ioc import IOCContainer

    _register_all_kafka_consumers(broker, IOCContainer)


def _register_all_kafka_consumers(broker: KafkaBroker, container: type) -> None:
    from delivery.core.ports.kafka_consumer import KafkaConsumer

    consumer_classes: typing.Final = KafkaConsumerRegistry.get_all_consumers()

    for consumer_class in consumer_classes:
        temp_instance = consumer_class.__new__(consumer_class)
        topic = temp_instance.topic
        group_id = temp_instance.group_id

        _create_subscriber(broker, container, consumer_class, topic, group_id)


def _create_subscriber(
    broker: KafkaBroker,
    container: type,
    consumer_class: type[KafkaConsumer],
    topic: str,
    group_id: str | None,
) -> None:
    subscriber_name: typing.Final = f"{consumer_class.__name__}_subscriber"

    async def subscriber(message: bytes) -> None:
        from delivery.core.application.services.kafka_consumer_resolver import KafkaConsumerResolver

        resolver: typing.Final = await container.kafka_consumer_resolver()
        consumer: typing.Final = resolver.get_consumer(consumer_class)
        await consumer.consume(message)

    subscriber.__name__ = subscriber_name

    broker.subscriber(topic, group_id=group_id)(subscriber)  # type: ignore[call-overload, untyped-decorator]
