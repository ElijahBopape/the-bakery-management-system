from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import auth, products, categories, orders

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="The Bakery Management System API",
    description="REST API for The Bakery — Polokwane. Built for XISD6329/w.",
    version="1.0.0",
)

# Allow all origins so the website and mobile app can connect freely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "The Bakery API is running"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
