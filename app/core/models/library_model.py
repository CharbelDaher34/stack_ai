from sqlmodel import Field, SQLModel, Relationship
import uuid
from .time_base import TimeBase
from typing import Optional, List
from datetime import datetime
from utils.pydantic_utils import make_optional

class LibraryBase(TimeBase):
    name: str
    written_by: str
    description: str
    production_date: datetime

class Library(LibraryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    indexed_at: Optional[datetime] = None
    
    # Use Relationship instead of relationship and string annotation
    documents: List["Document"] = Relationship(back_populates="library")
    
class LibraryCreate(LibraryBase):
    pass

class LibraryRead(LibraryBase):
    id: uuid.UUID

@make_optional
class LibraryUpdate(LibraryBase):
    pass
