from .time_base import TimeBase
from sqlmodel import Field, SQLModel, Relationship
import uuid
from typing import List
from utils.pydantic_utils import make_optional

class DocumentBase(TimeBase):
    name: str
    library_id: uuid.UUID = Field(foreign_key="library.id",ondelete="CASCADE")

class Document(DocumentBase, table=True,ondelete="CASCADE"):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Use Relationship instead of relationship and string annotations
    library: "Library" = Relationship(back_populates="documents")
    chunks: List["Chunk"] = Relationship(back_populates="document")

class DocumentCreate(DocumentBase):
    pass

class DocumentRead(DocumentBase):
    id: uuid.UUID

@make_optional
class DocumentUpdate(DocumentBase):
    pass