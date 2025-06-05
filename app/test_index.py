import time
from infrastructure.indexing.build_index import IndexBuilder
from services.chunk_service import ChunkService
from services.document_service import DocumentService
from services.library_service import LibraryService
from core.db import get_session
from scripts.populate_db import create_sample_data
from core.models import Chunk
def test_index_builder():
    session = next(get_session())
    index_builder = IndexBuilder(session)
    index_builder.build_index(index_type="linear")
    result = index_builder.search_index("transformers", 1)
    print(result)
  
    print("--------------------------------\n\n")
  
    index_builder.build_index(index_type="ball_tree")
    result = index_builder.search_index("transformers", 1)
    print(result)
    
create_sample_data(num_libraries=10, docs_per_library=10, chunks_per_doc=40)


test_index_builder()


