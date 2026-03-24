import typing

from fastapi import APIRouter

from delivery.adapters.input.http.controllers import (
    create_courier_router,
    create_order_router,
    get_couriers_router,
    get_orders_router,
)


def create_router() -> APIRouter:
    router: typing.Final = APIRouter(prefix="/api/v1")

    router.include_router(create_order_router)
    router.include_router(create_courier_router)
    router.include_router(get_couriers_router)
    router.include_router(get_orders_router)

    return router
