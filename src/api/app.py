from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import flow_router

from src.config.logger import setup_logging
from src.services.database.connection import initialize_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Service initialization complete")
    print("Database initialized")
    initialize_database() 
    yield
    print("Shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="MarketFlow API",
        lifespan=lifespan
    )
    
    # CORS setup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # register routes
    app.include_router(flow_router, prefix="/api")
    
    return app

setup_logging()
# export FastAPI instance
app = create_app()