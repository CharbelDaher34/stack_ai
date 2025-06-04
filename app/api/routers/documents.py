import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from core.db import get_session
from core.models import Document, DocumentCreate, DocumentRead, DocumentUpdate # Adjusted import path
from services.document_service import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)

def get_document_service(session: Session = Depends(get_session)) -> DocumentService:
    return DocumentService(session)

@router.post("/", response_model=DocumentRead)
def create_document(
    document_create: DocumentCreate,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Create a new document.
    """
    # The service returns Document, but endpoint might prefer DocumentRead
    # Assuming DocumentRead is the appropriate response model here.
    # If Document is preferred, change response_model to Document.
    created_doc = document_service.create_document(document_create=document_create)
    return DocumentRead.model_validate(created_doc) 

@router.get("/{document_id}", response_model=DocumentRead)
def read_document(
    document_id: uuid.UUID,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Get a specific document by its ID.
    """
    db_document = document_service.get_document(document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentRead.model_validate(db_document)

@router.get("/library/{library_id}", response_model=List[DocumentRead])
def read_documents_by_library(
    library_id: uuid.UUID,
    skip: int = 0,
    limit: int = Query(default=100, lte=1000),
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Get all documents for a specific library.
    """
    documents = document_service.get_documents_by_library(library_id=library_id, skip=skip, limit=limit)
    return [DocumentRead.model_validate(doc) for doc in documents]

@router.get("/", response_model=List[DocumentRead])
def read_all_documents(
    skip: int = 0,
    limit: int = Query(default=100, lte=1000),
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Get all documents with pagination.
    """
    documents = document_service.get_all_documents(skip=skip, limit=limit)
    return [DocumentRead.model_validate(doc) for doc in documents]

@router.put("/{document_id}", response_model=DocumentRead)
def update_document_endpoint(
    document_id: uuid.UUID,
    document_update: DocumentUpdate,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Update a document.
    """
    updated_document = document_service.update_document(document_id=document_id, document_update=document_update)
    if updated_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentRead.model_validate(updated_document)

@router.delete("/{document_id}", response_model=dict)
def delete_document_endpoint(
    document_id: uuid.UUID,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Delete a document and all its associated chunks.
    """
    if not document_service.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found or could not be deleted")
    return {"message": "Document and its chunks deleted successfully"}

@router.delete("/library/{library_id}", response_model=dict)
def delete_documents_by_library_endpoint(
    library_id: uuid.UUID,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Delete all documents in a library and their chunks.
    """
    deleted_count = document_service.delete_documents_by_library(library_id)
    # No specific check for deleted_count == 0 here, as service handles underlying logic.
    # Service might return 0 if library was empty or not found.
    return {"message": f"Successfully deleted {deleted_count} documents and their associated chunks from library {library_id}"}
