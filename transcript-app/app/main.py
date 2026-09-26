"""FastAPI application factory."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.core import paths
from app.core.config import load_dotenv
from app.db import store
from app.routes import api, pages
from app.services.worker import get_worker

logger = logging.getLogger("app")


def configure_logging() -> None:
    paths.ensure_directories()
    handler = RotatingFileHandler(
        paths.log_path(), maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        root.addHandler(handler)
    root.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    configure_logging()
    store.configure()
    store.init_db()
    recovered = store.mark_running_as_interrupted()
    if recovered:
        logger.warning("Marked %s interrupted transcript(s) from a previous run", recovered)
    worker = get_worker()
    worker.start()
    logger.info("Taglish Transcriber %s ready", __version__)
    try:
        yield
    finally:
        worker.stop()
        store.close()


def create_app() -> FastAPI:
    app = FastAPI(title="Taglish Transcriber", version=__version__, lifespan=lifespan)
    app.include_router(api.router)
    app.include_router(pages.router)
    app.mount(
        "/static", StaticFiles(directory=str(paths.web_dir() / "static")), name="static"
    )

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Something went wrong. Check app.log for details."},
        )

    return app


app = create_app()
