from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError, AuthenticationError
from app.db.session import engine
from app.models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Creates missing tables on startup. Will be replaced by Alembic migrations later.
    Base.metadata.create_all(engine)
    yield


async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    """Turns domain errors raised by services into HTTP responses."""
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, AuthenticationError) else None
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message}, headers=headers)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, handle_app_error)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
