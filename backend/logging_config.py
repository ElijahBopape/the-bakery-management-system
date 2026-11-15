"""
Central logging setup for The Bakery API.

Every module gets its logger with `get_logger(__name__)`, so each log line says which part
of the API wrote it (e.g. `bakery.routers.auth`). Lines go to standard output because that
is what the hosting platform collects: on Vercel they appear under Project -> Logs, and
locally they print in the terminal running uvicorn.

Level is set with the LOG_LEVEL environment variable (default INFO). Use DEBUG locally to
also see read-only calls such as listing products.

Privacy (POPIA): passwords, tokens and full email addresses are never logged. Use
`mask_email()` when a log line has to identify who an event was about.

Reference: Python Software Foundation (2024) "Logging HOWTO", Python 3.12 documentation.
Available at: https://docs.python.org/3/howto/logging.html (Accessed: 12 November 2026).
"""
import logging
import os
import sys

_CONFIGURED = False


def setup_logging() -> None:
    """Configure the shared 'bakery' logger once (safe to call more than once)."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler(sys.stdout)
    # Example line: 2026-11-12 22:41:03 INFO bakery.routers.auth | Login succeeded user_id=13 role=customer
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    )

    root = logging.getLogger("bakery")
    root.setLevel(level)
    root.addHandler(handler)
    root.propagate = False  # stop uvicorn's own handlers printing every line twice
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a child of the 'bakery' logger, e.g. get_logger(__name__) -> bakery.routers.auth."""
    setup_logging()
    return logging.getLogger(name if name.startswith("bakery") else f"bakery.{name}")


def mask_email(email: str) -> str:
    """Hide most of an email address for logs: 'thabo@gmail.com' -> 't***@gmail.com'."""
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[:1]}***@{domain}"
