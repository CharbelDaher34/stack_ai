import time
from infrastructure.indexing.build_index import IndexBuilder
from services.chunk_service import ChunkService
from services.document_service import DocumentService
from services.library_service import LibraryService
from core.db import get_session, create_db_and_tables
from scripts.populate_db import create_sample_data
from core.models import Chunk
print("Starting test_index_builder")
def test_index_builder():
    session = next(get_session())
    index_types=["linear","ball_tree"]
    index_builder = IndexBuilder(session,index_types)
    
    for index_type in index_types:
        result=index_builder.search_index("transformers", 1,index_type)
        print([chunk.text+"\n" for chunk in result])
    
create_db_and_tables(delete_tables=True)
create_sample_data(num_libraries=2, docs_per_library=2, chunks_per_doc=2)


test_index_builder()

