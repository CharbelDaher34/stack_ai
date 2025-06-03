from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = "sqlite:///./test.db" # In-memory SQLite for now, can be changed later

engine = create_engine(DATABASE_URL, echo=False) # echo=True for logging SQL queries

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