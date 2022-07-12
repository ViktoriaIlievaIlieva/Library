from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection


def get_connection():
    path_to_database: str = "D:\\Programming\\my_databases\\Personal.Library.db"
    engine: Engine = create_engine(f"sqlite:///{path_to_database}")
    connection: Connection = engine.connect()
    return connection
