import uuid
from typing import List,Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session,Field
from pydantic import BaseModel
from core.db import get_session
from core.models.chunk_model import Chunk, ChunkCreate, ChunkUpdate, ChunkRead, ChunkCreateRequest
from services.chunk_service import ChunkService
from infrastructure.indexing.build_index import IndexBuilder

router = APIRouter(
    prefix="/chunks",
    tags=["chunks"],
    responses={404: {"description": "Not found"}},
)

print("Indexing...")
index_manager = IndexBuilder(next(get_session()),["ball_tree","linear"])
print("Indexing done")

def get_chunk_service(session: Session = Depends(get_session)) -> ChunkService:
    return ChunkService(session)


 

@router.post("/", response_model=ChunkRead)
def create_chunk(
    chunk_create: ChunkCreateRequest,
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Create a new chunk.
    """
    try:
        chunk = chunk_service.create_chunk(chunk_create=chunk_create)
        print(f"Chunk created: {chunk.id}")
        index_manager.add_vector(chunk.embedding,chunk.id)
        print(f"Vector added to index: {chunk.id}")
        return chunk
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/random", response_model=str)
def create_random_chunk(
    text: str,
    chunk_service: ChunkService = Depends(get_chunk_service),
):
    """
    Create a new chunk.
    """
    try:
 
        index_manager.add_vector_by_text(text,random_chunk=True)
        print(f"Vector added to index: {text}")
        return "Added"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{chunk_id}", response_model=ChunkRead)
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

@router.get("/document/{document_id}", response_model=List[ChunkRead])
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

@router.get("/", response_model=List[ChunkRead])
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

@router.put("/{chunk_id}", response_model=ChunkRead)
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
    index_manager.add_vector(updated_chunk.embedding,updated_chunk.id)
    
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

class SearchResponse(BaseModel):
    list_of_chunks: Dict[str,List[str]]

@router.post("/search", response_model=SearchResponse)
def search_chunks(
    query: str,
    k: int = 10,
    index_types: List[str] = Query(default=["ball_tree", "linear"]),
):
    """
    Search for chunks using different index types.
    Returns a dictionary with index type as key and list of chunks as value.
    """
    dict_of_results = {}
    for index_type in index_types:
        dict_of_results[index_type] = [chunk.text for chunk in index_manager.search_index(query, k, index_type)]
    return SearchResponse(list_of_chunks=dict_of_results)

