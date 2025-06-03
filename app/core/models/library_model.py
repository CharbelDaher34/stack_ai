from sqlmodel import Field, SQLModel
import uuid
from core.models.time_base import TimeBase
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import relationship
from core.models.document_model import Document

class LibraryBase(TimeBase):
    name: str

class Library(LibraryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    indexed_at: Optional[datetime] = None
    
    documents: List["Document"] = relationship("Document", back_populates="library")
