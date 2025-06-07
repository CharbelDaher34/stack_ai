import uuid
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session

from core.db import get_session
from core.models import Library, LibraryCreate, LibraryRead
from services.library_service import LibraryService

from api.routers.chunks import index_manager

router = APIRouter(
    prefix="/libraries",
    tags=["libraries"],
    responses={404: {"description": "Not found"}},
)

# Dependency to get LibraryService
def get_library_service(session: Session = Depends(get_session)) -> LibraryService:
    return LibraryService(session)

@router.post("/", response_model=LibraryRead, status_code=status.HTTP_201_CREATED)
def create_library(
    library_create: LibraryCreate,
    service: LibraryService = Depends(get_library_service)
):
    """
    Create a new library.
    """
    # Add any API-level validation or pre-processing here if needed
    db_library = service.create_library(library_create)
    return db_library

@router.get("/", response_model=List[LibraryRead])
def read_libraries(
    skip: int = 0,
    limit: int = 100,
    service: LibraryService = Depends(get_library_service)
):
    """
    Retrieve all libraries.
    """
    libraries = service.get_libraries(skip=skip, limit=limit)
    return libraries

@router.get("/{library_id}", response_model=LibraryRead)
def read_library(
    library_id: uuid.UUID,
    service: LibraryService = Depends(get_library_service)
):
    """
    Retrieve a specific library by its ID.
    """
    db_library = service.get_library(library_id)
    if db_library is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Library not found")
    return db_library

@router.put("/{library_id}", response_model=LibraryRead)
def update_library(
    library_id: uuid.UUID,
    library_update: LibraryCreate, # Using LibraryCreate for update for now
    service: LibraryService = Depends(get_library_service)
):
    """
    Update a specific library.
    """
    updated_library = service.update_library(library_id, library_update)
    if updated_library is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Library not found")
    return updated_library

@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_library(
    library_id: uuid.UUID,
    service: LibraryService = Depends(get_library_service)
):
    """
    Delete a specific library and its associated documents and chunks.
    """
    result = service.delete_library(library_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Library not found")

    chunks_ids_deleted, documents_ids_deleted, library_deleted = result
    
    if library_deleted is None:
        raise HTTPException(status_code=500, detail="Failed to delete library.")

    for chunk_id in chunks_ids_deleted:
        index_manager.delete_vector(chunk_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)