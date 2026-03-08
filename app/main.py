from typing import List

from fastapi import FastAPI

from app.config.handlers import get_exception_handlers
from app.routers.impl.audio_router import AudioRouter
from app.routers.impl.internal_config_router import InternalConfigRouter
from app.routers.impl.internal_events_router import InternalEventsRouter
from app.routers.router_wrapper import RouterWrapper

exception_handlers = get_exception_handlers()
routers: List[RouterWrapper] = [
    AudioRouter(),
    InternalEventsRouter(),
    InternalConfigRouter()
]

app = FastAPI()

for exc, handler in exception_handlers:
    app.add_exception_handler(exc, handler)

for router in routers:
    app.include_router(router.get_fastapi_router())