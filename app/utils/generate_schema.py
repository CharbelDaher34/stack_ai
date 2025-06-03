#!python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy_schemadisplay import create_schema_graph
from core.db import engine
from sqlmodel import SQLModel
def generate_schema_diagram(output_path: str = 'dbschema.png'):
    """
    Generate a schema diagram for the current database models.
    Args:
        output_path (str): Path to save the generated PNG file.
    """
    graph = create_schema_graph(
        metadata=SQLModel.metadata,
        show_datatypes=True,
        show_indexes=True,
        rankdir='LR',
        concentrate=True,
        engine=engine
    )
    graph.write_png(output_path)
  
if __name__ == "__main__":
    generate_schema_diagram()