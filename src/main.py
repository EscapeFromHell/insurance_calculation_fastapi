import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.api_v1 import api_router
from src.config import settings
from src.core.db import create_start_app_handler, create_stop_app_handler

root_router = APIRouter()


def get_application() -> FastAPI:
    app = FastAPI(title="Insurance Calculation FastAPI")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_event_handler("startup", create_start_app_handler())
    app.add_event_handler("shutdown", create_stop_app_handler())
    app.include_router(api_router, prefix=settings.API_V1_STR)
    app.include_router(root_router)

    return app


app = get_application()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")
