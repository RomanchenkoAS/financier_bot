from fastapi import FastAPI
from loguru import logger

from .routers.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Financier Bot API")
    app.include_router(health_router)
    return app


app = create_app()


def run() -> None:
    """CLI entrypoint: uv run financier-api"""
    logger.info("Starting API server on http://0.0.0.0:8000")
    import uvicorn

    uvicorn.run("financier_bot.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
