from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import numpy as np
import os
import time

from discord_bot.contracts.ports import DatabasePort

# FIX AND SIMPLIFIE
# Detect container to choose default host
IN_DOCKER = os.path.exists("/.dockerenv")
DEFAULT_URI_DOCKER = "mongodb://root:example@mongo:27017/"
DEFAULT_URI_LOCAL = "mongodb://root:example@localhost:27017/"

# FIX THIS AND SIMPLIFIE
# Connection settings (read from environment; provide sensible defaults)
MONGO_URI = os.getenv("MONGO_URI", DEFAULT_URI_DOCKER if IN_DOCKER else DEFAULT_URI_LOCAL)
DB_NAME = os.getenv("DB_NAME", "discord_bot_db")
MONGO_CONNECT_TIMEOUT_SEC = int(os.getenv("MONGO_CONNECT_TIMEOUT_SEC", "10"))
MONGO_MAX_RETRIES = int(os.getenv("MONGO_MAX_RETRIES", "5"))
MONGO_RETRY_INTERVAL_SEC = float(os.getenv("MONGO_RETRY_INTERVAL_SEC", "1.5"))

_client: MongoClient | None = None
_db = None

def _init_global_connection():
    global _client, _db
    if _client is not None:
        return
    start = time.time()
    last_err = None
    for attempt in range(1, MONGO_MAX_RETRIES + 1):
        try:
            _client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=int(MONGO_CONNECT_TIMEOUT_SEC * 1000),
            )
            # Force server selection (raises if not reachable)
            _client.admin.command("ping")
            _db = _client[DB_NAME]
            return
        except Exception as e:
            last_err = e
            _client = None
            if time.time() - start > MONGO_CONNECT_TIMEOUT_SEC:
                break
            time.sleep(MONGO_RETRY_INTERVAL_SEC)
    raise ConnectionFailure(f"Mongo connection failed after {MONGO_MAX_RETRIES} attempts: {last_err}")

# Initialize once at import
try:
    _init_global_connection()
except ConnectionFailure:
    # Allow lazy retry later inside DBMS if initial import happens before Mongo is ready
    pass


# EXPAND THIS AS NEEDED
class DBMS(DatabasePort):
    """
    MongoDB adapter implementing DatabasePort.
    Provides CRUD operations plus random entry selection.
    """

    def __init__(self):
        if _client is None:
            _init_global_connection()
        self.client = _client
        self.db = _db

    def _collection(self, table: str):
        if self.db is None:
            _init_global_connection()
            self.db = _db
        return self.db[table]

    def get_table_size(self, table: str, category: str | None = None) -> int:
        query = {"category": category} if category is not None else {}
        return self._collection(table).count_documents(query)

    def get_random_entry(self, table: str, category: str | None) -> dict:
        query = {"category": category} if category is not None else {}
        size = self.get_table_size(table, category)
        if size == 0:
            return {}
        random_index = int(np.random.randint(0, size))
        cursor = self._collection(table).find(query).skip(random_index).limit(1)
        for entry in cursor:
            return entry
        return {}

    def get_data(self, table: str, query: dict) -> list[dict]:
        return [doc for doc in self._collection(table).find(query)]

    def insert_data(self, table: str, data: dict) -> bool:
        result = self._collection(table).insert_one(data)
        return result.acknowledged

    def update_data(self, table: str, query: dict, data: dict) -> bool:
        result = self._collection(table).update_many(query, {"$set": data})
        return result.acknowledged

    def delete_data(self, table: str, query: dict) -> bool:
        result = self._collection(table).delete_many(query)
        return result.acknowledged
