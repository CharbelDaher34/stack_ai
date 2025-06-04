from datetime import datetime
from sqlmodel import SQLModel, Field


class TimeBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
