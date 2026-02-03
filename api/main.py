import time
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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

    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    BASE_DIR = Path(__file__).resolve().parent.parent
    UI_DIR = BASE_DIR / "ui"
    STATIC_DIR = UI_DIR / "static"

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


    def serve_index():
        index_path = UI_DIR / "index.html"
        if not index_path.exists():
            return HTMLResponse(
                content="<h1>UI not found</h1><p>index.html is missing.</p>",
                status_code=500,
            )
        return HTMLResponse(
            content=index_path.read_text(encoding="utf-8"),
            media_type="text/html",
        )

    @app.get("/", response_class=HTMLResponse)
    async def root():
        return serve_index()

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def spa_fallback(full_path: str):
        # Allow API and docs routes to behave normally
        if full_path.startswith(("query", "docs", "openapi", "static")):
            return HTMLResponse(status_code=404)

        return serve_index()

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