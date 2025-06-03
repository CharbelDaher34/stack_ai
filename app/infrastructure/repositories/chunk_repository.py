import uuid
from typing import List, Optional
from sqlmodel import Session, select
from app.core.models.models import Chunk


class ChunkRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, chunk: Chunk) -> Chunk:
        self.session.add(chunk)
        self.session.commit()
        self.session.refresh(chunk)
        return chunk
    
    def get(self, chunk_id: uuid.UUID) -> Optional[Chunk]:
        return self.session.get(Chunk, chunk_id)
    
    def get_by_document_id(self, document_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Chunk]:
        statement = select(Chunk).where(Chunk.document_id == document_id).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Chunk]:
        statement = select(Chunk).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    def update(self, chunk: Chunk) -> Chunk:
        self.session.add(chunk)
        self.session.commit()
        self.session.refresh(chunk)
        return chunk
    
    def delete(self, chunk_id: uuid.UUID) -> bool:
        chunk = self.session.get(Chunk, chunk_id)
        if chunk:
            self.session.delete(chunk)
            self.session.commit()
            return True
        return False
    
    def delete_by_document_id(self, document_id: uuid.UUID) -> int:
        statement = select(Chunk).where(Chunk.document_id == document_id)
        chunks = self.session.exec(statement).all()
        count = len(chunks)
        for chunk in chunks:
            self.session.delete(chunk)
        self.session.commit()
        return count