from core.db import create_db_and_tables, create_sample_data

def initialize_db():
    create_db_and_tables()
    create_sample_data(num_libraries=10, docs_per_library=10, chunks_per_doc=10)

initialize_db()