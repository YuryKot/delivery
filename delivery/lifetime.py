import contextlib
import typing

import fastapi

from delivery.ioc import IOCContainer


@contextlib.asynccontextmanager
async def run_lifespan(application: fastapi.FastAPI) -> typing.AsyncIterator[None]:
    yield
    await IOCContainer.tear_down()
