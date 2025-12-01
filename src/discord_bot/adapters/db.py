from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.database import Database
import numpy as np
import os

from discord_bot.contracts.ports import DatabasePort

IN_DOCKER = os.path.exists("/.dockerenv")
DEFAULT_URI_DOCKER = "mongodb://root:example@mongo:27017/"
DEFAULT_URI_LOCAL = "mongodb://root:example@localhost:27017/"

class DBMS(DatabasePort):
    def __init__(self, uri: str | None = None, db_name: str | None = None): # FIX db_name parameter unused
        self.uri = uri or os.getenv("MONGO_URI", DEFAULT_URI_DOCKER if IN_DOCKER else DEFAULT_URI_LOCAL)
        self.db_name = "swp_discord_bot"
        self.client: MongoClient | None = None
        self.db: Database | None = None

    def connect(self):
        if self.client is not None:
            return
        try:
            self.client = MongoClient(self.uri)
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
        except Exception as e:
            self.client = None
            self.db = None
            raise ConnectionFailure(f"Mongo connect failed (uri={self.uri}): {e}")

    def _collection(self, table: str):
        if self.db is None:
            raise RuntimeError("DBMS not connected. Call connect() first.")
        return self.db[table]

    def get_table_size(self, table: str, category: str | None = None) -> int:
        query = {"category": category} if category is not None else {}
        return self._collection(table).count_documents(query)

    def get_random_entry(self, table: str, category: str | None) -> dict:
        query = {"category": category} if category is not None else {}
        size = self.get_table_size(table, category)
        if size == 0:
            return {}
        idx = int(np.random.randint(0, size))
        cursor = self._collection(table).find(query).skip(idx).limit(1)
        for doc in cursor:
            return doc
        return {}

    def get_data(self, table: str, query: dict) -> list[dict]:
        return [d for d in self._collection(table).find(query)]

    def insert_data(self, table: str, data: dict) -> bool:
        return self._collection(table).insert_one(data).acknowledged

    def update_data(self, table: str, query: dict, data: dict) -> bool:
        return self._collection(table).update_many(query, {"$set": data}).acknowledged

    def delete_data(self, table: str, query: dict) -> bool:
        return self._collection(table).delete_many(query).acknowledged
