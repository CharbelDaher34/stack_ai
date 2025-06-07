import pytest
from sqlmodel import Session
from infrastructure.indexing.build_index import IndexBuilder
from services.chunk_service import ChunkService
from services.document_service import DocumentService
from services.library_service import LibraryService
from core.db import get_session, create_db_and_tables
from scripts.populate_db import create_sample_data
from core.models import Chunk
import time
from faker import Faker

@pytest.fixture(scope="module")
def db_session():
    """Fixture to create a new database and tables for the test module."""
    print("🔧 Setting up database session fixture...")
    create_db_and_tables(delete_tables=False)
    session = next(get_session())
    print("✅ Database session created successfully")
    yield session
    print("🧹 Tearing down database session fixture...")
    # Teardown can be added here if needed, e.g., closing session
    # but get_session with 'with' statement handles it.

@pytest.fixture(scope="module")
def index_builder(db_session: Session):
    """Fixture to create an IndexBuilder instance."""
    print("🏗️ Creating IndexBuilder fixture...")
    index_types = ["linear", "ball_tree"]
    builder = IndexBuilder(db_session, index_types)
    print(f"✅ IndexBuilder created with index types: {index_types}")
    return builder

def test_add_vector_to_index(index_builder: IndexBuilder):
    """Test adding a vector to the index."""
    print("\n🧪 Running test_add_vector_to_index...")
    print("📝 Adding vector with text 'transformers' and id 'test_id'")
    
    index_builder.add_vector_by_text("transformers")
    print("✅ Vector added to index successfully")
    
    print("🔍 Searching for 'transformers' in linear index...")
    result = index_builder.search_index("transformers", 1, "linear")
    print(f"📊 Search result: {result}")
    print(f"📈 Number of results found: {len(result)}")
    
    assert len(result) > 0, f"Expected at least 1 result, got {len(result)}"
    
    if result:
        result_text = result[0].text.lower()
        print(f"🔤 First result text (lowercase): '{result_text}'")
        assert "transformers" in result_text, f"Expected 'transformers' in result text, got: '{result_text}'"
        print("✅ Text assertion passed")
    
    print("✅ test_add_vector_to_index completed successfully\n")

def test_index_builder_search_linear(index_builder: IndexBuilder):
    """Test searching the linear index."""
    print("\n🧪 Running test_index_builder_search_linear...")
    print("🔍 Searching for 'transformers' in linear index (k=1)...")
    
    result = index_builder.search_index("transformers", 1, "linear")
    print(f"📊 Linear search result: {result}")
    print(f"📈 Number of results found: {len(result)}")
    
    assert len(result) > 0, f"Expected at least 1 result from linear search, got {len(result)}"
    
    if result:
        print(f"🔤 First result text: '{result[0].text}'")
        # Uncommented the assertion for better testing
        result_text = result[0].text.lower()
        assert "transformers" in result_text, f"Expected 'transformers' in result text, got: '{result_text}'"
        print("✅ Text assertion passed")
    
    print("✅ test_index_builder_search_linear completed successfully\n")

def test_index_builder_search_ball_tree(index_builder: IndexBuilder):
    """Test searching the ball_tree index."""
    print("\n🧪 Running test_index_builder_search_ball_tree...")
    print("🔍 Searching for 'transformers' in ball_tree index (k=1)...")
    
    result = index_builder.search_index("transformers", 1, "ball_tree")
    print(f"📊 Ball tree search result: {result}")
    print(f"📈 Number of results found: {len(result)}")
    
    assert len(result) > 0, f"Expected at least 1 result from ball_tree search, got {len(result)}"
    
    if result:
        print(f"🔤 First result text: '{result[0].text}'")
        # Uncommented the assertion for better testing
        result_text = result[0].text.lower()
        assert "transformers" in result_text, f"Expected 'transformers' in result text, got: '{result_text}'"
        print("✅ Text assertion passed")
    
    print("✅ test_index_builder_search_ball_tree completed successfully\n")

def test_multiple_searches(index_builder: IndexBuilder):
    """Test multiple searches to ensure index consistency."""
    print("\n🧪 Running test_multiple_searches...")
    
    search_terms = ["transformers", "machine learning", "neural networks"]
    
    for term in search_terms:
        print(f"🔍 Searching for '{term}' in both indices...")
        
        linear_result = index_builder.search_index(term, 2, "linear")
        ball_tree_result = index_builder.search_index(term, 2, "ball_tree")
        
        print(f"📊 Linear results for '{term}': {len(linear_result)} items")
        print(f"📊 Ball tree results for '{term}': {len(ball_tree_result)} items")
        
        # Both indices should return some results (assuming data exists)
        if linear_result:
            print(f"🔤 Linear first result: '{linear_result[0].text[:50]}...'")
        if ball_tree_result:
            print(f"🔤 Ball tree first result: '{ball_tree_result[0].text[:50]}...'")
    
    print("✅ test_multiple_searches completed successfully\n")


def test_index_builder_delete_vector(index_builder: IndexBuilder):
    """Test deleting a vector from the index."""
    fake = Faker()
    text = fake.text()
    print("\n🧪 Running test_index_builder_delete_vector...")
    print(f"📝 Adding vector with text '{text}' and id 'test_id'")
    index_builder.add_vector_by_text(text)
    print("✅ Vector added to index successfully")
    
    print(f"🔍 Searching for '{text}' in linear index...")
    result = index_builder.search_index(text, 1, "linear")
    print(f"📊 Search result in linear index: {[chunk.text for chunk in result]}")
    
    print(f"🔍 Searching for '{text}' in ball tree index...")
    result = index_builder.search_index(text, 1, "ball_tree")
    print(f"📊 Search result in ball tree index: {[chunk.text for chunk in result]}")
    
    print("🔍 Deleting vector with id 'test_id'")
    index_builder.delete_vector(result[0].id)
    print("✅ Vector deleted from index successfully")
    
    print(f"🔍 Searching for '{text}' in linear index...")
    result = index_builder.search_index(text, 1, "linear")
    print(f"📊 Search result in linear index: {[chunk.text for chunk in result]}")
    
    assert text not in [chunk.text for chunk in result], f"Expected '{text}' not to be in results, got {len(result)}"
    result = index_builder.search_index(text, 1, "ball_tree")
    print(f"📊 Search result in ball tree index: {[chunk.text for chunk in result]}")
    assert text not in [chunk.text for chunk in result], f"Expected '{text}' not to be in results, got {len(result)}"
    
    print("✅ test_index_builder_delete_vector completed successfully\n")
    