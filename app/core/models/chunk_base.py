from sqlmodel import Field, SQLModel
import uuid
from core.models.time_base import TimeBase
from typing import List
from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy.orm import relationship

class ChunkBase(TimeBase):
    text: str
    embedding: List[float] = Field(sa_column=Column(JSON))
    document_id: uuid.UUID = Field(foreign_key="document.id")

class Chunk(ChunkBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document=relationship("Document", back_populates="chunks")