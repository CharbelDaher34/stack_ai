from fastapi import FastAPI
from core.db import create_db_and_tables
from api.routers import libraries_router, documents_router, chunks_router
print("Starting app...")
app = FastAPI(
    title="VectorDB API",
    description="API for indexing and querying documents in a Vector Database.",
    version="0.1.0"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

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
    uvicorn.run(app, host="0.0.0.0", port=8018)