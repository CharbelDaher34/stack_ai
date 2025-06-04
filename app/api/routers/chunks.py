import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from core.db import get_session
from core.models.chunk_model import Chunk, ChunkCreate, ChunkUpdate
from services.chunk_service import ChunkService

router = APIRouter(
    prefix="/chunks",
    tags=["chunks"],
    responses={404: {"description": "Not found"}},
)

def get_chunk_service(session: Session = Depends(get_session)) -> ChunkService:
    return ChunkService(session)

@router.post("/", response_model=Chunk)
def create_chunk(
    chunk_create: ChunkCreate,
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Create a new chunk.
    """
    try:
        return chunk_service.create_chunk(chunk_create=chunk_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{chunk_id}", response_model=Chunk)
def read_chunk(
    chunk_id: uuid.UUID,
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Get a specific chunk by its ID.
    """
    db_chunk = chunk_service.get_chunk(chunk_id)
    if db_chunk is None:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return db_chunk

@router.get("/document/{document_id}", response_model=List[Chunk])
def read_chunks_by_document(
    document_id: uuid.UUID,
    skip: int = 0,
    limit: int = Query(default=100, lte=1000),
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Get all chunks for a specific document.
    """
    chunks = chunk_service.get_chunks_by_document(document_id=document_id, skip=skip, limit=limit)
    return chunks

@router.get("/", response_model=List[Chunk])
def read_all_chunks(
    skip: int = 0,
    limit: int = Query(default=100, lte=1000),
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Get all chunks with pagination.
    """
    chunks = chunk_service.get_all_chunks(skip=skip, limit=limit)
    return chunks

@router.put("/{chunk_id}", response_model=Chunk)
def update_chunk_endpoint(
    chunk_id: uuid.UUID,
    chunk_update: ChunkUpdate,
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Update a chunk.
    """
    updated_chunk = chunk_service.update_chunk(chunk_id=chunk_id, chunk_update=chunk_update)
    if updated_chunk is None:
        raise HTTPException(status_code=404, detail="Chunk not found")
    return updated_chunk

@router.delete("/{chunk_id}", response_model=dict)
def delete_chunk_endpoint(
    chunk_id: uuid.UUID,
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Delete a chunk.
    """
    if not chunk_service.delete_chunk(chunk_id):
        raise HTTPException(status_code=404, detail="Chunk not found or could not be deleted")
    return {"message": "Chunk deleted successfully"}

@router.delete("/document/{document_id}", response_model=dict)
def delete_chunks_by_document_endpoint(
    document_id: uuid.UUID,
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Delete all chunks for a specific document.
    """
    deleted_count = chunk_service.delete_chunks_by_document(document_id)
    if deleted_count == 0:
        # This could mean the document had no chunks, or the document_id itself was not found.
        # Depending on desired behavior, you might not raise an error here.
        # For now, we'll assume it's okay if no chunks were deleted.
        pass
    return {"message": f"Successfully deleted {deleted_count} chunks for document {document_id}"}
