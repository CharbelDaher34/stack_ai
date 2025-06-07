from typing import List, Optional
import uuid
from datetime import datetime,timezone
from sqlmodel import Session, select
from core.models import Library, LibraryCreate, LibraryRead # Assuming LibraryUpdate will be similar to LibraryCreate for now
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

    def update_library(self, library_id: uuid.UUID, library_update_data: LibraryCreate) -> Optional[Library]:
        db_library = self.session.get(Library, library_id)
        if not db_library:
            return None
        
        # Update library fields
        library_data = library_update_data.model_dump(exclude_unset=True)
        for key, value in library_data.items():
            setattr(db_library, key, value)
        
   
        # Update the updated_at timestamp
        db_library.updated_at = datetime.now(timezone.utc)
        
        self.session.add(db_library)
        self.session.commit()
        self.session.refresh(db_library)
        return db_library

    def delete_library(self, library_id: uuid.UUID) -> Optional[Library]:
        db_library = self.session.get(Library, library_id)
        if not db_library:
            return None        
        self.session.delete(db_library)
        self.session.commit()
        return db_library