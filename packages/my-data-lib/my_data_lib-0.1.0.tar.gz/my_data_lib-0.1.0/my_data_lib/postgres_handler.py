from typing import Optional
import pandas as pd
import psycopg2
import sqlalchemy
import os
from my_data_lib.logger import Logger

class PostgresHandler:
    def __init__(self, connection_string=None, table_name=None, engine=None):
        self.table_name = table_name
        if engine:
            self.engine = engine
        else:
            self.engine = create_engine(connection_string)
        self.logger = Logger()

    def read(self) -> pd.DataFrame:
        self.logger.info(f"Lendo dados da tabela PostgreSQL: {self.table_name}")
        try:
            df = pd.read_sql_table(self.table_name, self.engine)
            self.logger.info(f"Leitura bem-sucedida. Linhas: {df.shape[0]}")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao ler tabela PostgreSQL: {e}")
            raise

    def write(self, df: pd.DataFrame):
        self.logger.info(f"Gravando dados na tabela PostgreSQL: {self.table_name}")
        try:
            df.to_sql(self.table_name, self.engine, if_exists="replace", index=False)
            self.logger.info("Gravação bem-sucedida.")
        except Exception as e:
            self.logger.error(f"Erro ao gravar tabela PostgreSQL: {e}")
            raise
