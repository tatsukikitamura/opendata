"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import get_allowed_origins
from routers import search, stations, ai, delays
from services.routing import initialize_graph
from db.database import engine
from db.models import Base

# Create tables if not exist
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - initialize resources on startup."""
    initialize_graph()
    yield


app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, tags=["Search"])
app.include_router(stations.router, tags=["Stations"])
app.include_router(ai.router, tags=["AI"])
app.include_router(delays.router)


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Train Route Search API is running"}
