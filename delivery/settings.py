import typing

import microbootstrap
import sqlalchemy


class Settings(microbootstrap.FastApiSettings):
    # Database settings
    database_dsn: str = ""
    database_connection_retries: int = 3

    # HTTP server settings
    http_port: int = 8082

    # Kafka settings
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "delivery-group"
    kafka_baskets_events_topic: str = "baskets.events"
    kafka_orders_events_topic: str = "orders.events"

    # gRPC settings
    geo_service_grpc_host: str = "0.0.0.0"
    geo_service_grpc_port: int = 5004

    @property
    def main_database_dsn(self) -> sqlalchemy.URL:
        original_parsed_url: typing.Final = sqlalchemy.make_url(self.database_dsn)
        return original_parsed_url.set(query=dict(original_parsed_url.query) | {"target_session_attrs": "read-write"})

    @property
    def replica_database_dsn(self) -> sqlalchemy.URL:
        original_parsed_url: typing.Final = sqlalchemy.make_url(self.database_dsn)
        return original_parsed_url.set(
            query=dict(original_parsed_url.query) | {"target_session_attrs": "prefer-standby"}
        )


settings: typing.Final = Settings()
