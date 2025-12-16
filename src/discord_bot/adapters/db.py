"""MongoDB-backed implementation of the `DatabasePort` interface."""

import numpy as np
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.database import Database

from discord_bot.contracts.ports import DatabasePort
from discord_bot.init.config_loader import DBConfigLoader

class DBMS(DatabasePort):
    def __init__(self, uri: str | None = None, db_name: str | None = None) -> None:
        self.uri = uri or DBConfigLoader.MONGO_URI
        self.db_name = db_name or DBConfigLoader.CV_DB_NAME
        self.client: MongoClient | None = None
        self.db: Database | None = None

    def connect(self, max_attempts: int = 10, delay_seconds: float = 2) -> None:
        if self.client is not None:
            return

        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                self.client = MongoClient(self.uri)
                self.client.admin.command("ping")
                self.db = self.client[self.db_name]
                return
            except Exception as error:
                self.client = None
                self.db = None
                last_error = error

                if attempt == max_attempts:
                    break
                time.sleep(delay_seconds)

        raise ConnectionFailure(f'Mongo connect failed after {max_attempts} attempts (uri={self.uri}): {last_error}')

    def _table(self, table_name: str):
        """Return the Mongo collection for the given table name.

        Args:
            table_name (str): Name of the collection/table.

        Returns:
            Collection: PyMongo collection object.

        Raises:
            RuntimeError: If called before a successful `connect`.
        """
        if self.db is None:
            raise RuntimeError("DBMS not connected. Call connect() first.")

        return self.db[table_name]

    def get_table_size(self, table_name: str, category: str | None = None) -> int:
        query = {"category": category} if category is not None else {}
        return self._table(table_name).count_documents(query)

    def get_random_entry(self, table_name: str, category: str | None) -> dict:
        query = {"category": category} if category is not None else {}
        size = self.get_table_size(table_name, category)
        if size == 0:
            return {}
        
        index = int(np.random.randint(0, size))
        # Use skip+limit to fetch a single random document efficiently.
        cursor = self._table(table_name).find(query).skip(index).limit(1)

        for document in cursor:
            return document
        return {}

    def get_data(self, table_name: str, query: dict) -> list[dict]:
        return [document for document in self._table(table_name).find(query)]

    def get_distinct_values(self, table_name: str, field: str) -> list[str]:
        return sorted(
            value for value in self._table(table_name).distinct(field)
            if value is not None
        )

    def insert_data(self, table_name: str, data: dict) -> bool:
        return self._table(table_name).insert_one(data).acknowledged

    def update_data(self, table_name: str, query: dict, data: dict) -> bool:
        return self._table(table_name).update_many(query, {"$set": data}).acknowledged

    def delete_data(self, table_name: str, query: dict) -> bool:
        return self._table(table_name).delete_many(query).acknowledged

    def upload_table(self, db_name: str, table_name: str, data: list[dict], drop_existing: bool = True) -> bool:
        if self.client is None:
            raise RuntimeError("DBMS not connected. Call connect() first.")

        try:
            target_db = self.client[db_name]
            table = target_db[table_name]

            if drop_existing:
                table.drop()

            if data:
                table.insert_many(data)
                return True
            return False

        except Exception as error:
            raise RuntimeError(f'Error uploading table: {error}')
