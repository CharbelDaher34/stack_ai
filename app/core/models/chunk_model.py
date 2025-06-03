from sqlmodel import Field, SQLModel, Relationship
import uuid
from .time_base import TimeBase
from typing import List
from sqlalchemy import JSON
from sqlalchemy import Column
from utils.pydantic_utils import make_optional

class ChunkBase(TimeBase):
    text: str
    embedding: List[float] = Field(sa_column=Column(JSON))
    document_id: uuid.UUID = Field(foreign_key="document.id")

class Chunk(ChunkBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Use Relationship instead of relationship and string annotation
    document: "Document" = Relationship(back_populates="chunks")
    
class ChunkCreate(ChunkBase):
    pass

class ChunkRead(ChunkBase):
    id: uuid.UUID

@make_optional
class ChunkUpdate(ChunkBase):
    pass