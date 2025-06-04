#!/usr/bin/env python3
"""
Script to populate the database with sample data using the service classes.
This script creates libraries, documents, and chunks to test the vector database functionality.
"""

import sys
import os
from datetime import datetime, timedelta
from sqlmodel import Session
from core.db import engine, create_db_and_tables
from core.models import LibraryCreate, DocumentCreate, ChunkCreate
from services.library_service import LibraryService
from services.document_service import DocumentService
from services.chunk_service import ChunkService


def create_sample_data():
    """Create sample libraries, documents, and chunks."""
    
    # Create database tables if they don't exist
    create_db_and_tables()
    
    with Session(engine) as session:
        # Initialize services
        library_service = LibraryService(session)
        document_service = DocumentService(session)
        chunk_service = ChunkService(session)
        
        print("🚀 Starting database population...")
        
        # Create sample libraries
        libraries_data = [
            {
                "name": "Machine Learning Research Papers",
                "written_by": "AI Research Team",
                "description": "A collection of cutting-edge machine learning research papers and publications",
                "production_date": datetime.now() - timedelta(days=30)
            },
            {
                "name": "Software Engineering Best Practices",
                "written_by": "Development Team",
                "description": "Documentation and guides on software engineering methodologies and best practices",
                "production_date": datetime.now() - timedelta(days=60)
            },
            {
                "name": "Data Science Tutorials",
                "written_by": "Data Science Team",
                "description": "Comprehensive tutorials and examples for data science techniques and tools",
                "production_date": datetime.now() - timedelta(days=15)
            }
        ]
        
        created_libraries = []
        for lib_data in libraries_data:
            library_create = LibraryCreate(**lib_data)
            library = library_service.create_library(library_create)
            created_libraries.append(library)
            print(f"✅ Created library: {library.name} (ID: {library.id})")
        
        # Create sample documents for each library
        documents_data = [
            # Documents for Machine Learning Research Papers
            {
                "name": "Deep Learning Fundamentals",
                "library_id": created_libraries[0].id,
                "content": [
                    "Deep learning is a subset of machine learning that uses artificial neural networks with multiple layers to model and understand complex patterns in data.",
                    "Convolutional Neural Networks (CNNs) are particularly effective for image recognition tasks, using convolutional layers to detect features.",
                    "Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTM) networks are designed to handle sequential data and time series.",
                    "Transformer architectures have revolutionized natural language processing with their attention mechanisms and parallel processing capabilities."
                ]
            },
            {
                "name": "Reinforcement Learning Applications",
                "library_id": created_libraries[0].id,
                "content": [
                    "Reinforcement learning involves training agents to make decisions by interacting with an environment and receiving rewards or penalties.",
                    "Q-learning is a model-free reinforcement learning algorithm that learns the quality of actions, telling an agent what action to take under what circumstances.",
                    "Policy gradient methods directly optimize the policy function that maps states to actions, often using neural networks as function approximators.",
                    "Deep Q-Networks (DQN) combine deep learning with Q-learning to handle high-dimensional state spaces in complex environments."
                ]
            },
            # Documents for Software Engineering Best Practices
            {
                "name": "Clean Code Principles",
                "library_id": created_libraries[1].id,
                "content": [
                    "Clean code is code that is easy to read, understand, and maintain. It follows consistent naming conventions and has clear structure.",
                    "Functions should be small and do one thing well. They should have descriptive names that clearly indicate their purpose.",
                    "Comments should explain why something is done, not what is done. The code itself should be self-explanatory.",
                    "Error handling should be comprehensive and graceful, providing meaningful error messages and recovery mechanisms."
                ]
            },
            {
                "name": "Test-Driven Development",
                "library_id": created_libraries[1].id,
                "content": [
                    "Test-Driven Development (TDD) is a software development approach where tests are written before the actual code implementation.",
                    "The TDD cycle follows Red-Green-Refactor: write a failing test, make it pass, then refactor the code for better design.",
                    "Unit tests should be fast, independent, repeatable, and focused on testing a single unit of functionality.",
                    "Integration tests verify that different components work together correctly, while end-to-end tests validate complete user workflows."
                ]
            },
            # Documents for Data Science Tutorials
            {
                "name": "Data Preprocessing Techniques",
                "library_id": created_libraries[2].id,
                "content": [
                    "Data preprocessing is a crucial step in data science that involves cleaning, transforming, and preparing raw data for analysis.",
                    "Handling missing values can be done through deletion, imputation with mean/median/mode, or using advanced techniques like KNN imputation.",
                    "Feature scaling techniques like normalization and standardization ensure that all features contribute equally to machine learning algorithms.",
                    "Categorical encoding methods such as one-hot encoding, label encoding, and target encoding convert categorical variables to numerical format."
                ]
            },
            {
                "name": "Statistical Analysis Methods",
                "library_id": created_libraries[2].id,
                "content": [
                    "Descriptive statistics provide summary measures of data including central tendency, variability, and distribution shape.",
                    "Hypothesis testing allows us to make inferences about populations based on sample data using statistical significance tests.",
                    "Correlation analysis measures the strength and direction of relationships between variables using Pearson, Spearman, or Kendall coefficients.",
                    "Regression analysis models relationships between dependent and independent variables, enabling prediction and inference."
                ]
            }
        ]
        
        created_documents = []
        for doc_data in documents_data:
            content = doc_data.pop("content")  # Remove content from doc_data
            document_create = DocumentCreate(**doc_data)
            document = document_service.create_document(document_create)
            created_documents.append((document, content))
            print(f"✅ Created document: {document.name} (ID: {document.id})")
        
        # Create chunks for each document
        total_chunks = 0
        for document, content_chunks in created_documents:
            for i, text in enumerate(content_chunks):
                chunk_create = ChunkCreate(
                    text=text,
                    document_id=document.id,
                    embedding=[]  # Will be generated by the service
                )
                chunk = chunk_service.create_chunk(chunk_create)
                total_chunks += 1
                print(f"✅ Created chunk {i+1} for document '{document.name}' (ID: {chunk.id})")
        
        print(f"\n🎉 Database population completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Libraries created: {len(created_libraries)}")
        print(f"   - Documents created: {len(created_documents)}")
        print(f"   - Chunks created: {total_chunks}")
        
        # Display library statistics
        print(f"\n📈 Library Statistics:")
        for library in created_libraries:
            stats = library_service.get_library_stats(library.id)
            if stats:
                print(f"   - {stats['library_name']}: {stats['document_count']} documents, {stats['chunk_count']} chunks")


def main():
    """Main function to run the database population script."""
    try:
        create_sample_data()
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 