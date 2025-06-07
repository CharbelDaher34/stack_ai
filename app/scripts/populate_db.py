#!/usr/bin/env python3
"""
Script to populate the database with sample data using the service classes.
This script creates libraries, documents, and chunks to test the vector database functionality.
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from sqlmodel import Session
from core.db import engine, create_db_and_tables
from core.models import LibraryCreate, DocumentCreate, ChunkCreate
from services.library_service import LibraryService
from services.document_service import DocumentService
from services.chunk_service import ChunkService
from faker import Faker
import random

fake = Faker()

def create_sample_data(num_libraries: int, docs_per_library: int, chunks_per_doc: int):
    """Create sample libraries, documents, and chunks."""
    
    
    with Session(engine) as session:
        library_service = LibraryService(session)
        document_service = DocumentService(session)
        chunk_service = ChunkService(session)
        
        print("🚀 Starting database population...")
        
        created_libraries = []
        for i in range(num_libraries):
            lib_data = {
                "name": fake.catch_phrase(),
                "written_by": fake.name(),
                "description": fake.text(max_nb_chars=120),
                "production_date": fake.date_time_between(start_date="-1y", end_date="now")
            }
            library_create = LibraryCreate(**lib_data)
            library = library_service.create_library(library_create)
            created_libraries.append(library)
            print(f"✅ Created library: {library.name} (ID: {library.id})")
        
        created_documents = []
        for library in created_libraries:
            for _ in range(docs_per_library):
                doc_data = {
                    "name": fake.sentence(nb_words=4).rstrip('.'),
                    "library_id": library.id
                }
                document_create = DocumentCreate(**doc_data)
                document = document_service.create_document(document_create)
                content_chunks = [fake.paragraph(nb_sentences=4) for _ in range(chunks_per_doc)]
                created_documents.append((document, content_chunks))
                print(f"✅ Created document: {document.name} (ID: {document.id})")

        total_chunks = 0
        for document, content_chunks in created_documents:
            for i, text in enumerate(content_chunks):
                chunk_create = ChunkCreate(
                    text=text,
                    document_id=document.id,
                    embedding=[]  # embedding to be added later
                )
                chunk = chunk_service.create_chunk(chunk_create)
                total_chunks += 1
                print(f"✅ Created chunk {i+1} for document '{document.name}' (ID: {chunk.id})")
        
        print(f"\n🎉 Database population completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Libraries created: {len(created_libraries)}")
        print(f"   - Documents created: {len(created_documents)}")
        print(f"   - Chunks created: {total_chunks}")
        
        print(f"\n📈 Library Statistics:")
        for library in created_libraries:
            stats = library_service.get_library_stats(library.id)
            if stats:
                print(f"   - {stats['library_name']}: {stats['document_count']} documents, {stats['chunk_count']} chunks")

def main():
    parser = argparse.ArgumentParser(description="Populate the vector database with fake data.")
    parser.add_argument("--libraries", type=int, required=True, help="Number of libraries to create")
    parser.add_argument("--docs", type=int, required=True, help="Number of documents per library")
    parser.add_argument("--chunks", type=int, required=True, help="Number of chunks per document")
    args = parser.parse_args()

    try:
        create_sample_data(args.libraries, args.docs, args.chunks)
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
