from typing import Optional
import pandas as pd
from pymongo import MongoClient
from my_data_lib.logger import Logger

class MongoDBHandler:
    def __init__(self, uri: str, database: str, collection: str):
        self.client = MongoClient(uri)
        self.collection = self.client[database][collection]
        self.logger = Logger()

    def read(self) -> pd.DataFrame:
        self.logger.info(f"Lendo dados do MongoDB, coleção: {self.collection.name}")
        try:
            data = list(self.collection.find())
            df = pd.DataFrame(data)
            self.logger.info(f"Leitura bem-sucedida. Linhas: {df.shape[0]}")
            return df
        except Exception as e:
            self.logger.error(f"Erro ao ler dados do MongoDB: {e}")
            raise

    def write(self, df: pd.DataFrame):
        self.logger.info(f"Gravando dados no MongoDB, coleção: {self.collection.name}")
        try:
            self.collection.delete_many({})
            self.collection.insert_many(df.to_dict(orient="records"))
            self.logger.info("Gravação bem-sucedida.")
        except Exception as e:
            self.logger.error(f"Erro ao gravar dados no MongoDB: {e}")
            raise
