
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine

DATABASE_URL = "sqlite:///./test.db"

# Create the engine without the 'foreign_keys' option
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# Enable foreign key constraints for SQLite
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def get_session():
    with Session(engine) as session:
        yield session



# Function to create DB and tables (call this from main.py on startup)
def create_db_and_tables():
    # Import all your models here so they are registered with SQLModel's metadata
    from core.models import Library, Document, Chunk 
    
    # This will create tables for all models that inherit from SQLModel
    # and have table=True
    SQLModel.metadata.create_all(engine) 