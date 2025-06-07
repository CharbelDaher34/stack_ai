from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import os
from typing import Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_env_var(key: str, default: Optional[str] = None) -> str:
    value = os.getenv(key, default)
    logger.info(f"Environment variable {key}: {value}")
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

# Get database configuration from environment variables
db_config = {
    "user": get_env_var("POSTGRES_USER", "charbel"),
    "password": get_env_var("POSTGRES_PASSWORD", "charbel"),
    "host": get_env_var("POSTGRES_HOST", "db"),
    "port": get_env_var("POSTGRES_PORT", "5432"),
    "db": get_env_var("POSTGRES_DB", "stack_ai")
}

logger.info(f"Final database configuration: {db_config}")

DATABASE_URL = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db']}"
logger.info(f"Database URL (with password masked): postgresql://{db_config['user']}:****@{db_config['host']}:{db_config['port']}/{db_config['db']}")

# Create the engine without the 'foreign_keys' option
engine = create_engine(
    DATABASE_URL,
    echo=False,
)

# # Enable foreign key constraints for SQLite
# @event.listens_for(engine, "connect")
# def enable_foreign_keys(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()

def get_session():
    with Session(engine) as session:
        yield session



# Function to create DB and tables (call this from main.py on startup)
def create_db_and_tables(delete_tables: bool = False):
    # Import all your models here so they are registered with SQLModel's metadata
    from core.models import Library, Document, Chunk 
    
    # This will create tables for all models that inherit from SQLModel
    # and have table=True
    if delete_tables:
        SQLModel.metadata.drop_all(engine)
        print("Tables dropped")
    SQLModel.metadata.create_all(engine) 
    print("Tables created")