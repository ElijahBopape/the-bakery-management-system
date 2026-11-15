"""
Database connection for The Bakery API (SQLAlchemy).

DATABASE_URL decides which database is used:
  - not set           -> a local SQLite file (bakery.db), handy for development and CI
  - postgresql://...  -> the hosted Neon PostgreSQL database (set by Vercel automatically)
get_db() opens one session per request and always closes it afterwards.

Reference: SQLAlchemy (2024) "Engine Configuration" and "Dealing with Disconnects" (pool_pre_ping),
SQLAlchemy 2.0 documentation. Available at: https://docs.sqlalchemy.org/en/20/core/engines.html and
https://docs.sqlalchemy.org/en/20/core/pooling.html#pool-disconnects (Accessed: 12 November 2026).
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bakery.db")

# Railway provides a DATABASE_URL with postgres:// — SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# pool_pre_ping: the hosted API runs as a serverless function on Vercel and Neon closes
# idle connections, so check each pooled connection is still alive before using it.
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
