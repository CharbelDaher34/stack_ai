from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routers import libraries_router, documents_router, chunks_router
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup event triggered.")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8018,workers=3)