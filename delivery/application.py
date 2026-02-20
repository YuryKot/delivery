import typing

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from microbootstrap.bootstrappers.fastapi import FastApiBootstrapper
from microbootstrap.config.fastapi import FastApiConfig
from starlette.middleware import Middleware
from that_depends import ContextScopes
from that_depends.providers import DIContextMiddleware

from delivery import lifetime
from delivery.exception_handlers import register_exception_handlers
from delivery.settings import settings


def build_app() -> FastAPI:
    app_config: typing.Final = FastApiConfig(
        default_response_class=UJSONResponse,
        lifespan=lifetime.run_lifespan,
        middleware=[
            Middleware(DIContextMiddleware, scope=ContextScopes.REQUEST),
        ],
    )
    application: typing.Final = FastApiBootstrapper(settings).configure_application(app_config).bootstrap()
    register_exception_handlers(application)
    return application


application: typing.Final = build_app()
