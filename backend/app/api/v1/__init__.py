from fastapi import APIRouter

from backend.app.api.v1 import (
    boms,
    components,
    events,
    gateways,
)


api_router = APIRouter()

api_router.include_router(components.router)
api_router.include_router(boms.router)
api_router.include_router(events.router)
api_router.include_router(gateways.router)


__all__ = [
    "api_router",
]