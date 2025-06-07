import uuid
from typing import List, Optional
from sqlmodel import Session, select
from core.models import Document


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, document: Document) -> Document:
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        return document
    
    def get(self, document_id: uuid.UUID) -> Optional[Document]:
        return self.session.get(Document, document_id)
    
    def get_by_library_id(self, library_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        statement = select(Document).where(Document.library_id == library_id).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        statement = select(Document).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    def update(self, document: Document) -> Document:
        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)
        return document
    
    def delete(self, document_id: uuid.UUID) -> bool:
        document = self.session.get(Document, document_id)
        if document:
            self.session.delete(document)
            self.session.commit()
            return True
        return False
    
    def delete_by_library_id(self, library_id: uuid.UUID) -> List[uuid.UUID]:
        statement = select(Document).where(Document.library_id == library_id)
        documents = self.session.exec(statement).all()
        document_ids=[document.id for document in documents]
        for document in documents:
            self.session.delete(document)
        self.session.commit()
        return document_ids