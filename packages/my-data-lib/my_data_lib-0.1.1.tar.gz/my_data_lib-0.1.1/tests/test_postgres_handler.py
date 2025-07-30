from unittest.mock import MagicMock, patch
import pytest
import pandas as pd
import psycopg2.extras
from my_data_lib.postgres_handler import PostgresHandler

class FakePostgresHandler(PostgresHandler):
    def __init__(self):
        self._dataframe = pd.DataFrame({
            "id": [1, 2],
            "nome": ["teste1", "teste2"]
        })

    def read(self):
        return self._dataframe.copy()

    def write(self, df):
        self._dataframe = df.copy()

def test_read_write_sem_conexao():
    handler = FakePostgresHandler()

    df_lido = handler.read()
    assert not df_lido.empty
    assert "nome" in df_lido.columns

    novo_df = pd.DataFrame({
        "id": [3],
        "nome": ["novo"]
    })
    handler.write(novo_df)

    df_depois = handler.read()
    assert df_depois.equals(novo_df)