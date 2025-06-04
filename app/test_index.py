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
    result = index_builder.search_index("Convolutional Neural Networks?", 1)
    for chunk_id, distance in result:
        chunk = ChunkService(session).get_chunk(chunk_id)
        document = DocumentService(session).get_document(chunk.document_id)
        library = LibraryService(session).get_library(document.library_id)
        print(f"\n\nLibrary: {library.name}, Document: {document.name}, Chunk: {chunk.text if chunk else 'Not found'}\n\n")
    print(result)

# create_sample_data()
test_index_builder()


