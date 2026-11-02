import time
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from eyes_backend.routes import scraping_router, scan_router
from eyes_backend.settings import get_settings

settings = get_settings()
req_logger = logging.getLogger("eyes_backend.requests")

app:FastAPI = FastAPI(
    title=settings.name,
    debug=settings.debug,
    version=settings.version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
        "http://localhost:1420"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(scraping_router)
app.include_router(scan_router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        ms = (time.perf_counter() - start) * 1000
        req_logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, status, ms)