from fastapi import FastAPI
from api.routes import router
from api.logging import setup_logging

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="UK Finance Domain Intelligence System",
        version="1.0.0",
        description="RAG-based question answering over UK financial reports",
    )

    app.include_router(router)

    return app


app = create_app()