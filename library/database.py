from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection


def get_connection():
    path_to_database: str = "C:\\Users\\capit\\Desktop\\books\\Personal.Library.db"
    engine: Engine = create_engine(f"sqlite:///{path_to_database}")
    connection: Connection = engine.connect()
    return connection
