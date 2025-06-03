from sqlmodel import Field, SQLModel
import uuid
from core.models.time_base import TimeBase
from sqlalchemy.orm import relationship
from typing import List

class DocumentBase(TimeBase):
    name: str
    library_id: uuid.UUID = Field(foreign_key="library.id")

class Document(DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    library=relationship("Library", back_populates="documents")
    chunks: List["Chunk"] = relationship("Chunk", back_populates="document")
