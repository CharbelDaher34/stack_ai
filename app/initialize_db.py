#!/usr/bin/env python3
"""
Database initialization script.
This script creates database tables and optionally populates them with sample data.
"""

import os
import sys
import logging
from sqlmodel import Session
from core.db import create_db_and_tables, engine
from scripts.populate_db import create_sample_data

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_tables_exist():
    """Check if tables already exist in the database."""
    from core.models import Library, Document, Chunk
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    required_tables = ['library', 'document', 'chunk']
    tables_exist = all(table in existing_tables for table in required_tables)
    
    logger.info(f"Existing tables: {existing_tables}")
    logger.info(f"Required tables: {required_tables}")
    logger.info(f"All tables exist: {tables_exist}")
    
    return tables_exist

def check_data_exists():
    """Check if data already exists in the database."""
    try:
        with Session(engine) as session:
            from core.models import Library
            from sqlmodel import select
            
            statement = select(Library)
            result = session.exec(statement).first()
            has_data = result is not None
            
            logger.info(f"Database has existing data: {has_data}")
            return has_data
    except Exception as e:
        logger.warning(f"Could not check for existing data: {e}")
        return False

def main():
    """Initialize the database with tables and optionally populate with sample data."""
    logger.info("🚀 Starting database initialization...")
    
    try:
        # Check if tables exist
        tables_exist = check_tables_exist()
        
        if not tables_exist:
            logger.info("📋 Creating database tables...")
            create_db_and_tables(delete_tables=False)
            logger.info("✅ Database tables created successfully")
        else:
            logger.info("✅ Database tables already exist")
        
     
        if not check_data_exists():
            logger.info("📊 Populating database with sample data...")
            num_libraries = 2
            docs_per_library = 2
            chunks_per_doc = 2
            
            create_sample_data(num_libraries, docs_per_library, chunks_per_doc)
            logger.info("✅ Sample data populated successfully")
        else:
            logger.info("✅ Database already contains data, skipping population")
          
        logger.info("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()