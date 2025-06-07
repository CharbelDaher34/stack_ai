import uuid
from typing import List, Optional
from sqlmodel import Session, select, func
from core.models import Chunk


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
    
    def get_by_document_id(self, document_id: uuid.UUID, skip: int = 0, limit: int = 100, for_indexing: bool = False) -> List[Chunk]:
        if for_indexing:
            statement = select(Chunk.id, Chunk.embedding).where(Chunk.document_id == document_id).offset(skip).limit(limit)
        else:
            statement = select(Chunk).where(Chunk.document_id == document_id).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    def get_all(self, skip: int = 0, limit: int = 100, for_indexing: bool = False) -> List[Chunk]:
        if for_indexing:
            statement = select(Chunk.id, Chunk.embedding).offset(skip).limit(limit)
        else:
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
    
    def delete_by_document_id(self, document_id: uuid.UUID) -> List[uuid.UUID]:
        statement = select(Chunk).where(Chunk.document_id == document_id)
        chunks = self.session.exec(statement).all()
        chunk_ids=[chunk.id for chunk in chunks]
        for chunk in chunks:
            self.session.delete(chunk)
        self.session.commit()
        return chunk_ids
    
    def get_random_document_id(self) -> uuid.UUID:
        chunks=self.get_all(limit=1)
       
        return chunks[0].document_id