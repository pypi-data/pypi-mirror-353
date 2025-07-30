from typing import Literal, Union, Optional
from .csv_handler import CSVHandler
from .postgres_handler import PostgresHandler
from .mongodb_handler import MongoDBHandler

def get_data_handler(
    source_type: Literal["csv", "postgres", "mongodb"],
    path: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    uri: Optional[str] = None,
    collection: Optional[str] = None
) -> Union[CSVHandler, PostgresHandler, MongoDBHandler]:
    if source_type == "csv":
        if not path:
            raise ValueError("O parâmetro 'path' é obrigatório para CSVHandler.")
        return CSVHandler(path=path)
    elif source_type == "postgres":
        if not all([host, port, database, user, password]):
            raise ValueError("Parâmetros obrigatórios para PostgresHandler: host, port, database, user, password.")
        return PostgresHandler(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
    elif source_type == "mongodb":
        if not all([uri, database, collection]):
            raise ValueError("Parâmetros obrigatórios para MongoDBHandler: uri, database, collection.")
        return MongoDBHandler(
            uri=uri,
            database=database,
            collection=collection
        )
    else:
        raise ValueError(f"Fonte de dados '{source_type}' não suportada.")