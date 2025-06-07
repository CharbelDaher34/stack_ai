from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.db import create_db_and_tables
from api.routers import libraries_router, documents_router, chunks_router
from scripts.populate_db import create_sample_data
print("Starting app...")

# --- Correct Lifespan Definition ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup event triggered.")
    # Run your database table creation logic here
    # If create_db_and_tables was an async function, you'd await it.
    # Since create_db_and_tables_sync is synchronous, just call it.
    create_db_and_tables(delete_tables=False)
    print("Database tables created.")
    # create_sample_data(num_libraries=3, docs_per_library=4, chunks_per_doc=20)
    yield # This yields control to the FastAPI application to start serving requests

    print("Application shutdown event triggered.")
    # Place cleanup code here if needed (e.g., closing connections, flushing logs)
    # For a simple SQLModel setup, explicit engine closing is often not required
    # as it's managed by the engine's lifecycle, but for more complex scenarios
    # or connection pools, you might need to clean up here.


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
    uvicorn.run(app, host="0.0.0.0", port=8018)