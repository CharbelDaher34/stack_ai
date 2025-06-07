#!/usr/bin/env python3
"""
Example usage of the Vector Database API Client SDK

This script demonstrates how to use the VectorDBClient SDK to interact
with the Vector Database API.
"""

from client_sdk import VectorDBClient, IndexType, VectorDBAPIError
from datetime import datetime


def main():
    """Main example function demonstrating SDK usage."""
    
    # Initialize the client
    print("🚀 Initializing Vector Database Client...")
    client = VectorDBClient(base_url="http://localhost:8018")
    
    try:
        # 1. Health Check
        print("\n📊 Checking API health...")
        health = client.health_check()
        print(f"✅ API Status: {health}")
        
        # 2. Create a Library
        print("\n📚 Creating a new library...")
        library = client.create_library(
            name="Machine Learning Research",
            written_by="AI Research Team",
            description="A collection of machine learning research papers and documents",
            production_date=datetime(2024, 1, 1)
        )
        print(f"✅ Created library: {library.name} (ID: {library.id})")
        
        # 3. Create Documents
        print("\n📄 Creating documents...")
        doc1 = client.create_document(
            name="Neural Networks Fundamentals",
            library_id=library.id
        )
        print(f"✅ Created document: {doc1.name} (ID: {doc1.id})")
        
        doc2 = client.create_document(
            name="Vector Databases Overview",
            library_id=library.id
        )
        print(f"✅ Created document: {doc2.name} (ID: {doc2.id})")
        
        # 4. Create Chunks
        print("\n📝 Creating chunks...")
        chunks_data = [
            ("Neural networks are computational models inspired by biological neural networks.", doc1.id),
            ("Deep learning uses multiple layers to progressively extract features from raw input.", doc1.id),
            ("Backpropagation is the algorithm used to train neural networks.", doc1.id),
            ("Vector databases store and index high-dimensional vectors for similarity search.", doc2.id),
            ("Embeddings represent text, images, or other data as dense vectors.", doc2.id),
            ("k-nearest neighbor search finds the most similar vectors in the database.", doc2.id),
        ]
        
        created_chunks = []
        for text, document_id in chunks_data:
            chunk = client.create_chunk(text=text, document_id=document_id)
            created_chunks.append(chunk)
            print(f"✅ Created chunk: {text[:50]}...")
        
        # 5. List all libraries
        print("\n📋 Listing all libraries...")
        all_libraries = client.get_all_libraries()
        for lib in all_libraries:
            print(f"  📚 {lib.name} by {lib.written_by}")
        
        # 6. Get documents in the library
        print(f"\n📄 Getting documents in library '{library.name}'...")
        library_docs = client.get_documents_by_library(library.id)
        for doc in library_docs:
            print(f"  📄 {doc.name}")
        
        # 7. Get chunks in a document
        print(f"\n📝 Getting chunks in document '{doc1.name}'...")
        doc_chunks = client.get_chunks_by_document(doc1.id)
        for chunk in doc_chunks:
            print(f"  📝 {chunk.text[:60]}...")
        
        # 8. Perform Vector Search
        print("\n🔍 Performing vector searches...")
        
        # Search with linear index
        search_results = client.search_chunks(
            query="neural networks and deep learning",
            k=3,
            index_types=[IndexType.LINEAR]
        )
        print(f"🔍 Linear search results:")
        for text in search_results.list_of_chunks.get("linear", []):
            print(f"  📝 {text}")
        
        # Search with ball tree index
        search_results = client.search_chunks(
            query="vector similarity search",
            k=3,
            index_types=[IndexType.BALL_TREE]
        )
        print(f"🔍 Ball tree search results:")
        for text in search_results.list_of_chunks.get("ball_tree", []):
            print(f"  📝 {text}")
        
        # Compare both index types
        print("\n🔍 Comparing search results from both index types...")
        comparison_results = client.search_chunks(
            query="machine learning algorithms",
            k=2,
            index_types=[IndexType.LINEAR, IndexType.BALL_TREE]
        )
        
        for index_type, results in comparison_results.list_of_chunks.items():
            print(f"  {index_type.upper()} index:")
            for text in results:
                print(f"    📝 {text}")
        
        # 9. Update operations
        print("\n✏️ Updating library description...")
        updated_library = client.update_library(
            library_id=library.id,
            description="Updated: A comprehensive collection of ML research with vector search capabilities"
        )
        print(f"✅ Updated library description")
        
        # 10. Use convenience method
        print("\n🏗️ Using convenience method to create complete hierarchy...")
        hierarchy = client.create_complete_hierarchy(
            library_name="Computer Vision Library",
            library_author="CV Research Team",
            library_description="Computer vision research and applications",
            document_name="Image Processing Techniques",
            chunk_texts=[
                "Convolutional neural networks are fundamental to computer vision.",
                "Image preprocessing includes normalization and augmentation techniques.",
                "Object detection identifies and localizes objects in images."
            ]
        )
        print(f"✅ Created complete hierarchy:")
        print(f"  📚 Library: {hierarchy['library'].name}")
        print(f"  📄 Document: {hierarchy['document'].name}")
        print(f"  📝 Chunks: {len(hierarchy['chunks'])} created")
        
        # 11. Advanced search with details
        print("\n🔍 Advanced search with detailed results...")
        detailed_results = client.search_and_get_details(
            query="computer vision and image processing",
            k=2,
            index_type=IndexType.LINEAR
        )
        
        for i, chunk in enumerate(detailed_results, 1):
            print(f"  {i}. {chunk.text}")
            print(f"     📄 Document ID: {chunk.document_id}")
            print(f"     🆔 Chunk ID: {chunk.id}")
        
        print("\n🎉 SDK demonstration completed successfully!")
        
    except VectorDBAPIError as e:
        print(f"❌ API Error: {e.message}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        if e.response_data:
            print(f"   Response Data: {e.response_data}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


def cleanup_example():
    """Example of how to clean up resources."""
    
    client = VectorDBClient(base_url="http://localhost:8000")
    
    try:
        print("\n🧹 Cleanup example...")
        
        # Get all libraries
        libraries = client.get_all_libraries()
        
        # Delete libraries created in this example
        for library in libraries:
            if "Example" in library.name or "Machine Learning Research" in library.name or "Computer Vision" in library.name:
                print(f"🗑️ Deleting library: {library.name}")
                client.delete_library(library.id)
                print(f"✅ Deleted library: {library.name}")
        
        print("✅ Cleanup completed!")
        
    except VectorDBAPIError as e:
        print(f"❌ Cleanup error: {e.message}")


def search_examples():
    """Examples of different search patterns."""
    
    client = VectorDBClient(base_url="http://localhost:8000")
    
    try:
        print("\n🔍 Search Examples...")
        
        # Example 1: Simple search
        results = client.search_chunks("machine learning", k=3)
        print(f"Simple search found {len(results.list_of_chunks.get('linear', []))} results")
        
        # Example 2: Search with specific index
        results = client.search_chunks(
            query="neural networks", 
            k=5, 
            index_types=[IndexType.BALL_TREE]
        )
        print(f"Ball tree search found {len(results.list_of_chunks.get('ball_tree', []))} results")
        
        # Example 3: Multi-index comparison
        results = client.search_chunks(
            query="vector database", 
            k=3, 
            index_types=[IndexType.LINEAR, IndexType.BALL_TREE]
        )
        
        linear_count = len(results.list_of_chunks.get('linear', []))
        ball_tree_count = len(results.list_of_chunks.get('ball_tree', []))
        print(f"Comparison: Linear={linear_count}, Ball Tree={ball_tree_count}")
        
    except VectorDBAPIError as e:
        print(f"❌ Search error: {e.message}")

def add_and_search():
    client = VectorDBClient(base_url="http://localhost:8018")
    library = client.create_library(
        name="Machine Learning Research",
        written_by="AI Research Team",
        description="A collection of machine learning research papers and documents",
        production_date=datetime(2024, 1, 1))
    doc1 = client.create_document(
        name="Neural Networks Fundamentals",
        library_id=library.id
    )
    doc2 = client.create_document(
        name="Vector Databases Overview",
        library_id=library.id
    )
    client.create_chunk(
        text="sdfsdfsdfsd.",
        document_id=doc1.id)
    
    results = client.search_chunks(
        query="choubaki and charbel is great.",
        k=3,
        index_types=[IndexType.LINEAR,IndexType.BALL_TREE]
    )
    print(results)
if __name__ == "__main__":
    print("🎯 Vector Database SDK Example")
    print("=" * 50)
    
    # Run main example
    main()
    
    # Uncomment to run search examples
    add_and_search()
    
    # Uncomment to run cleanup (be careful - this deletes data!)
    # cleanup_example() 