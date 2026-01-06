
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import search, stations, ai
from services.routing import initialize_graph
from db.database import engine
from db.models import Base

# Create tables if not exist
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize route graph on startup
    initialize_graph()
    yield


app = FastAPI(lifespan=lifespan)

import os

# CORS configuration
# origins_str = os.getenv("ALLOWED_ORIGINS", "*")
# origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

# For safety, default to "*" (allow all) only if explicitly set or if ALLOWED_ORIGINS is missing/empty in dev.
# In production, ALLOWED_ORIGINS should be set to "https://<user>.github.io".
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, tags=["Search"])

app.include_router(stations.router, tags=["Stations"])

app.include_router(ai.router, tags=["AI"])


@app.get("/")
def read_root():
    return {"message": "Train Route Search API is running"}
