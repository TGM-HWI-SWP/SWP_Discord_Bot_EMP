"""Unit tests for critical DBMS operations that can fail."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import Mock, MagicMock, patch
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, DuplicateKeyError

from discord_bot.adapters.db import DBMS


class TestCriticalDBMSOperations(unittest.TestCase):
    """Test critical database operations where failures can occur."""

    def setUp(self):
        """Set up test fixtures."""
        self.dbms = DBMS(uri="mongodb://test-uri", db_name="test_db")

    # ==================== CRITICAL FUNCTION 1: connect() ====================
    
    @patch('discord_bot.adapters.db.MongoClient')
    def test_connect_successful_connection(self, mock_mongo_client):
        """Test successful database connection."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client

        # Act
        self.dbms.connect()

        # Assert
        mock_mongo_client.assert_called_once_with("mongodb://test-uri")
        mock_client.admin.command.assert_called_once_with("ping")
        self.assertIsNotNone(self.dbms.client)
        self.assertIsNotNone(self.dbms.db)

    @patch('discord_bot.adapters.db.MongoClient')
    @patch('discord_bot.adapters.db.time.sleep')
    def test_connect_fails_after_max_retries(self, mock_sleep, mock_mongo_client):
        """Test connection failure after maximum retry attempts."""
        # Arrange
        mock_mongo_client.side_effect = ServerSelectionTimeoutError("Connection timeout")

        # Act & Assert
        with self.assertRaises(ConnectionFailure) as context:
            self.dbms.connect(max_attempts=3, delay_seconds=0.1)

        self.assertIn("failed after 3 attempts", str(context.exception))
        self.assertEqual(mock_mongo_client.call_count, 3)
        self.assertIsNone(self.dbms.client)
        self.assertIsNone(self.dbms.db)

    @patch('discord_bot.adapters.db.MongoClient')
    @patch('discord_bot.adapters.db.time.sleep')
    def test_connect_succeeds_on_second_attempt(self, mock_sleep, mock_mongo_client):
        """Test connection succeeds after initial failure (retry logic works)."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.side_effect = [
            Exception("First attempt fails"),
            mock_client  # Second attempt succeeds
        ]

        # Act
        self.dbms.connect(max_attempts=3)

        # Assert
        self.assertEqual(mock_mongo_client.call_count, 2)
        self.assertIsNotNone(self.dbms.client)
        mock_sleep.assert_called_once()

    @patch('discord_bot.adapters.db.MongoClient')
    def test_connect_idempotent_when_already_connected(self, mock_mongo_client):
        """Test connect() doesn't reconnect if already connected."""
        # Arrange
        mock_client = MagicMock()
        self.dbms.client = mock_client  # Simulate already connected

        # Act
        self.dbms.connect()

        # Assert
        mock_mongo_client.assert_not_called()  # Should not create new connection

    # ==================== CRITICAL FUNCTION 2: upload_table() ====================

    @patch('discord_bot.adapters.db.MongoClient')
    def test_upload_table_successful_upload_with_data(self, mock_mongo_client):
        """Test successful table upload with data."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_table = MagicMock()
        mock_client.__getitem__.return_value.__getitem__.return_value = mock_table
        
        test_data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]

        # Act
        result = self.dbms.upload_table("test_db", "test_table", test_data, drop_existing=True)

        # Assert
        self.assertTrue(result)
        mock_table.drop.assert_called_once()
        mock_table.insert_many.assert_called_once_with(test_data)

    @patch('discord_bot.adapters.db.MongoClient')
    def test_upload_table_returns_false_with_empty_data(self, mock_mongo_client):
        """Test upload_table returns False when data list is empty."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()

        # Act
        result = self.dbms.upload_table("test_db", "test_table", [], drop_existing=True)

        # Assert
        self.assertFalse(result)

    @patch('discord_bot.adapters.db.MongoClient')
    def test_upload_table_preserves_existing_data_when_drop_false(self, mock_mongo_client):
        """Test upload_table doesn't drop existing data when drop_existing=False."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_table = MagicMock()
        mock_client.__getitem__.return_value.__getitem__.return_value = mock_table
        
        test_data = [{"id": 1, "name": "New Item"}]

        # Act
        result = self.dbms.upload_table("test_db", "test_table", test_data, drop_existing=False)

        # Assert
        self.assertTrue(result)
        mock_table.drop.assert_not_called()
        mock_table.insert_many.assert_called_once()

    def test_upload_table_raises_error_when_not_connected(self):
        """Test upload_table raises RuntimeError when database not connected."""
        # Arrange
        dbms = DBMS()  # Not connected

        # Act & Assert
        with self.assertRaises(RuntimeError) as context:
            dbms.upload_table("test_db", "test_table", [{"data": "test"}])
        
        self.assertIn("not connected", str(context.exception))

    @patch('discord_bot.adapters.db.MongoClient')
    def test_upload_table_handles_insert_failure(self, mock_mongo_client):
        """Test upload_table handles insert_many failure gracefully."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_table = MagicMock()
        mock_table.insert_many.side_effect = Exception("Insert failed")
        mock_client.__getitem__.return_value.__getitem__.return_value = mock_table

        # Act & Assert
        with self.assertRaises(RuntimeError) as context:
            self.dbms.upload_table("test_db", "test_table", [{"id": 1}])
        
        self.assertIn("Error uploading table", str(context.exception))

    # ==================== CRITICAL FUNCTION 3: insert_data() ====================

    @patch('discord_bot.adapters.db.MongoClient')
    def test_insert_data_successful_insertion(self, mock_mongo_client):
        """Test successful data insertion."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_insert_result = MagicMock()
        mock_insert_result.acknowledged = True
        mock_collection.insert_one.return_value = mock_insert_result
        self.dbms.db.__getitem__.return_value = mock_collection

        test_data = {"user_id": 123, "name": "Test User"}

        # Act
        result = self.dbms.insert_data("users", test_data)

        # Assert
        self.assertTrue(result)
        mock_collection.insert_one.assert_called_once_with(test_data)

    @patch('discord_bot.adapters.db.MongoClient')
    def test_insert_data_returns_false_on_unacknowledged_write(self, mock_mongo_client):
        """Test insert_data returns False when write is not acknowledged."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_insert_result = MagicMock()
        mock_insert_result.acknowledged = False
        mock_collection.insert_one.return_value = mock_insert_result
        self.dbms.db.__getitem__.return_value = mock_collection

        # Act
        result = self.dbms.insert_data("users", {"data": "test"})

        # Assert
        self.assertFalse(result)

    @patch('discord_bot.adapters.db.MongoClient')
    def test_insert_data_handles_duplicate_key_error(self, mock_mongo_client):
        """Test insert_data when duplicate key constraint is violated."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_collection.insert_one.side_effect = DuplicateKeyError("Duplicate key error")
        self.dbms.db.__getitem__.return_value = mock_collection

        # Act & Assert
        with self.assertRaises(DuplicateKeyError):
            self.dbms.insert_data("users", {"_id": "existing_id"})

    # ==================== CRITICAL FUNCTION 4: update_data() ====================

    @patch('discord_bot.adapters.db.MongoClient')
    def test_update_data_successful_update(self, mock_mongo_client):
        """Test successful data update."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_update_result = MagicMock()
        mock_update_result.acknowledged = True
        mock_collection.update_many.return_value = mock_update_result
        self.dbms.db.__getitem__.return_value = mock_collection

        query = {"user_id": 123}
        update_data = {"name": "Updated Name"}

        # Act
        result = self.dbms.update_data("users", query, update_data)

        # Assert
        self.assertTrue(result)
        mock_collection.update_many.assert_called_once_with(query, {"$set": update_data})

    @patch('discord_bot.adapters.db.MongoClient')
    def test_update_data_updates_multiple_documents(self, mock_mongo_client):
        """Test update_data can update multiple matching documents."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_update_result = MagicMock()
        mock_update_result.acknowledged = True
        mock_update_result.modified_count = 3
        mock_collection.update_many.return_value = mock_update_result
        self.dbms.db.__getitem__.return_value = mock_collection

        # Act
        result = self.dbms.update_data("users", {"status": "active"}, {"last_seen": "2026-01-09"})

        # Assert
        self.assertTrue(result)

    @patch('discord_bot.adapters.db.MongoClient')
    def test_update_data_with_empty_query_updates_all(self, mock_mongo_client):
        """Test update_data with empty query updates all documents."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_update_result = MagicMock()
        mock_update_result.acknowledged = True
        mock_collection.update_many.return_value = mock_update_result
        self.dbms.db.__getitem__.return_value = mock_collection

        # Act
        result = self.dbms.update_data("statistics", {}, {"connected_guilds": 5})

        # Assert
        self.assertTrue(result)
        mock_collection.update_many.assert_called_once_with({}, {"$set": {"connected_guilds": 5}})

    # ==================== CRITICAL FUNCTION 5: delete_data() ====================

    @patch('discord_bot.adapters.db.MongoClient')
    def test_delete_data_successful_deletion(self, mock_mongo_client):
        """Test successful data deletion."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_delete_result = MagicMock()
        mock_delete_result.acknowledged = True
        mock_delete_result.deleted_count = 1
        mock_collection.delete_many.return_value = mock_delete_result
        self.dbms.db.__getitem__.return_value = mock_collection

        query = {"user_id": 123}

        # Act
        result = self.dbms.delete_data("users", query)

        # Assert
        self.assertTrue(result)
        mock_collection.delete_many.assert_called_once_with(query)

    @patch('discord_bot.adapters.db.MongoClient')
    def test_delete_data_returns_true_even_when_no_matches(self, mock_mongo_client):
        """Test delete_data returns True even when no documents match."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_delete_result = MagicMock()
        mock_delete_result.acknowledged = True
        mock_delete_result.deleted_count = 0
        mock_collection.delete_many.return_value = mock_delete_result
        self.dbms.db.__getitem__.return_value = mock_collection

        # Act
        result = self.dbms.delete_data("users", {"user_id": 999999})

        # Assert
        self.assertTrue(result)

    @patch('discord_bot.adapters.db.MongoClient')
    def test_delete_data_with_empty_query_deletes_all(self, mock_mongo_client):
        """Test delete_data with empty query deletes all documents (dangerous!)."""
        # Arrange
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        self.dbms.connect()
        
        mock_collection = MagicMock()
        mock_delete_result = MagicMock()
        mock_delete_result.acknowledged = True
        mock_delete_result.deleted_count = 100
        mock_collection.delete_many.return_value = mock_delete_result
        self.dbms.db.__getitem__.return_value = mock_collection

        # Act
        result = self.dbms.delete_data("temp_data", {})

        # Assert
        self.assertTrue(result)
        mock_collection.delete_many.assert_called_once_with({})


if __name__ == "__main__":
    unittest.main()
