from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.db import create_db_and_tables
from api.routers import libraries_router, documents_router, chunks_router
from scripts.populate_db import create_sample_data
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables before importing routers
logger.info("Creating database tables...")
create_db_and_tables(delete_tables=False)
logger.info("Database tables created successfully")

# Now import routers after tables are created
from api.routers import libraries_router, documents_router, chunks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup event triggered.")
    # Tables are already created, no need to create them here
    yield
    logger.info("Application shutdown event triggered.")

app = FastAPI(
    title="VectorDB API",
    description="API for indexing and querying documents in a Vector Database.",
    version="0.1.0",
    lifespan=lifespan
)

# Include routers
app.include_router(libraries_router)
app.include_router(documents_router)
app.include_router(chunks_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

# If you have other routers, you would include them here, for example:
# from app.api.routers import documents as documents_router
# from app.api.routers import chunks as chunks_router
#
# app.include_router(documents_router.router, prefix="/api/v1/documents", tags=["Documents"])
# app.include_router(chunks_router.router, prefix="/api/v1/chunks", tags=["Chunks"]) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018, workers=3)