import logging

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from test_project_fastapi.settings import settings
from test_project_fastapi.web.api.router import api_router
from importlib import metadata

from test_project_fastapi.web.lifespan import lifespan_setup
from pathlib import Path

from fastapi.staticfiles import StaticFiles

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="test_project_fastapi",
        version=metadata.version("test_project_fastapi"),
        lifespan=lifespan_setup,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")

    return app
