"""
The Bakery Management System - REST API entry point.

This file builds the FastAPI app that both the website (bake/) and the Android app
(mobile-app/) talk to. It:
  1. sets up logging (logging_config.py),
  2. creates the database tables if they do not exist yet,
  3. allows cross-origin requests so the website can call the API from any address,
  4. logs every request (method, path, status code, time taken) and any crash,
  5. plugs in the routers: /auth, /categories, /products, /orders.

Live:  https://the-bakery-api.vercel.app   (interactive docs at /docs)
Local: uvicorn main:app --reload --port 8000

References:
  FastAPI (2024) "Middleware" and "CORS (Cross-Origin Resource Sharing)", FastAPI documentation.
  Available at: https://fastapi.tiangolo.com/tutorial/middleware/ and
  https://fastapi.tiangolo.com/tutorial/cors/ (Accessed: 12 November 2026).
"""
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from logging_config import get_logger, setup_logging

setup_logging()
log = get_logger("bakery.main")

from database import engine, Base, DATABASE_URL  # noqa: E402  (import after logging is ready)
from routers import auth, products, categories, orders  # noqa: E402

# Create all tables on startup (does nothing if they already exist).
Base.metadata.create_all(bind=engine)
# Log which kind of database is in use, never the connection string (it holds the password).
log.info("API starting - database: %s", "PostgreSQL" if DATABASE_URL.startswith("postgresql") else "SQLite")

app = FastAPI(
    title="The Bakery Management System API",
    description="REST API for The Bakery — Polokwane. Built for XISD6329/w.",
    version="1.1.0",
)

# Allow all origins so the website (opened from any address) and the mobile app can connect.
# Safe here because sign-in uses a Bearer token in a header, not cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log one line per request, e.g.
        INFO bakery.main | POST /auth/login -> 200 (84 ms) [req a1b2c3d4]
    The short request id is also sent back in the X-Request-ID header, so an error a
    teammate sees in the app or browser can be matched to the exact line in the logs.
    Server errors (500) log the full stack trace instead of a normal line.
    """
    request_id = uuid.uuid4().hex[:8]
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        ms = (time.perf_counter() - start) * 1000
        log.exception("%s %s -> 500 crashed (%.0f ms) [req %s]", request.method, request.url.path, ms, request_id)
        return JSONResponse(
            status_code=500,
            content={"detail": "Something went wrong on the server. Please try again.", "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )

    ms = (time.perf_counter() - start) * 1000
    # 4xx = the caller did something wrong (warning); everything else is normal traffic (info).
    level = log.warning if 400 <= response.status_code < 500 else log.info
    level("%s %s -> %d (%.0f ms) [req %s]", request.method, request.url.path, response.status_code, ms, request_id)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/", tags=["health"])
def root():
    """Simple 'is it up?' check used in screenshots and by teammates."""
    return {"status": "ok", "message": "The Bakery API is running"}


@app.get("/health", tags=["health"])
def health():
    """Health check for the hosting platform and CI (the GitHub Actions smoke test waits on this)."""
    return {"status": "healthy"}
