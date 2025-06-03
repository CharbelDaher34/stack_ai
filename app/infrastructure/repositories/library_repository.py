from typing import List, Optional
import uuid
from datetime import datetime
from sqlmodel import Session, select
from app.core.models.models import Library, LibraryCreate, LibraryRead # Assuming LibraryUpdate will be similar to LibraryCreate for now
from core.db import get_session # We'll need a way to get a DB session

class LibraryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_library(self, library_create: LibraryCreate) -> Library:
        db_library = Library.model_validate(library_create)
        self.session.add(db_library)
        self.session.commit()
        self.session.refresh(db_library)
        return db_library

    def get_library(self, library_id: uuid.UUID) -> Optional[Library]:
        return self.session.get(Library, library_id)

    def get_libraries(self, skip: int = 0, limit: int = 100) -> List[Library]:
        statement = select(Library).offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()

    def update_library(self, library_id: uuid.UUID, library_update_data: LibraryCreate, indexed_at: Optional[datetime] = None) -> Optional[Library]:
        db_library = self.session.get(Library, library_id)
        if not db_library:
            return None
        
        # Update library fields
        library_data = library_update_data.model_dump(exclude_unset=True)
        for key, value in library_data.items():
            setattr(db_library, key, value)
        
        # Update indexed_at if provided
        if indexed_at is not None:
            db_library.indexed_at = indexed_at
        
        # Update the updated_at timestamp
        db_library.updated_at = datetime.utcnow()
        
        self.session.add(db_library)
        self.session.commit()
        self.session.refresh(db_library)
        return db_library

    def delete_library(self, library_id: uuid.UUID) -> Optional[Library]:
        db_library = self.session.get(Library, library_id)
        if not db_library:
            return None
        
        # Store the library data before deletion
        library_copy = Library(
            id=db_library.id,
            name=db_library.name,
            created_at=db_library.created_at,
            updated_at=db_library.updated_at,
            indexed_at=db_library.indexed_at
        )
        
        self.session.delete(db_library)
        self.session.commit()
        
        return library_copy 