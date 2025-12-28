import time
import uuid
import logging
from fastapi import FastAPI, Request

from api.routes import router
from api.logging import setup_logging

logger = logging.getLogger("finance-dis")

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="UK Finance Domain Intelligence System",
        version="1.0.0",
        description="RAG-based question answering over UK financial reports",
    )

    @app.middleware("http")
    async def request_logger(request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time.time()

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            status = 500
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            raise

        latency_ms = int((time.time() - start) * 1000)

        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status": status,
                "latency_ms": latency_ms,
            },
        )

        return response

    app.include_router(router)

    return app


app = create_app()