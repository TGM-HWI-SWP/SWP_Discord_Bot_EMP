"""Unit tests for critical DBLoader CSV import operations."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open

from discord_bot.init.db_loader import DBLoader


class TestCriticalDBLoaderOperations(unittest.TestCase):
    """Test critical database loader operations that can fail."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('discord_bot.init.db_loader.DBMS'):
            self.loader = DBLoader()

    # ==================== CRITICAL: CSV Import with Encoding Issues ====================

    @patch('discord_bot.init.db_loader.DBMS')
    @patch('builtins.open', new_callable=mock_open, read_data='id,dish,category\n1,Pizza Margherita,Italian\n2,Sushi,Japanese')
    @patch('discord_bot.init.db_loader.Path.glob')
    def test_import_tables_successful_csv_import(self, mock_glob, mock_file, mock_dbms):
        """Test successful CSV import to database."""
        # Arrange
        loader = DBLoader()
        mock_csv_file = MagicMock()
        mock_csv_file.stem = "dishes"
        mock_glob.return_value = [mock_csv_file]
        
        loader.cv_dbms.get_table_size.return_value = 0
        loader.cv_dbms.upload_table.return_value = True

        # Act
        loader.import_tables(force_reload=False)

        # Assert
        loader.cv_dbms.connect.assert_called_once()
        loader.cv_dbms.upload_table.assert_called_once()
        args = loader.cv_dbms.upload_table.call_args[0]
        self.assertEqual(len(args[2]), 2)  # 2 rows imported

    @patch('discord_bot.init.db_loader.DBMS')
    @patch('builtins.open', side_effect=FileNotFoundError("CSV file not found"))
    @patch('discord_bot.init.db_loader.Path.glob')
    def test_import_tables_handles_missing_csv_file(self, mock_glob, mock_file, mock_dbms):
        """Test import_tables handles missing CSV file gracefully."""
        # Arrange
        loader = DBLoader()
        mock_csv_file = MagicMock()
        mock_csv_file.stem = "missing_table"
        mock_glob.return_value = [mock_csv_file]
        
        loader.cv_dbms.get_table_size.return_value = 0

        # Act & Assert
        with self.assertRaises(FileNotFoundError):
            loader.import_tables(force_reload=False)

    @patch('discord_bot.init.db_loader.DBMS')
    @patch('builtins.open', new_callable=mock_open, read_data='id,dish,category\n1,Café Crème,French\n2,Crème Brûlée,French')
    @patch('discord_bot.init.db_loader.Path.glob')
    def test_import_tables_handles_utf8_characters(self, mock_glob, mock_file, mock_dbms):
        """Test import_tables correctly handles UTF-8 special characters."""
        # Arrange
        loader = DBLoader()
        mock_csv_file = MagicMock()
        mock_csv_file.stem = "dishes"
        mock_glob.return_value = [mock_csv_file]
        
        loader.cv_dbms.get_table_size.return_value = 0
        loader.cv_dbms.upload_table.return_value = True

        # Act
        loader.import_tables(force_reload=False)

        # Assert
        mock_file.assert_called_with(unittest.mock.ANY, "r", encoding="utf-8")

    @patch('discord_bot.init.db_loader.DBMS')
    @patch('builtins.open', new_callable=mock_open, read_data='id,dish,category\n5,Pizza,Italian\ninvalid_id,Pasta,Italian')
    @patch('discord_bot.init.db_loader.Path.glob')
    def test_import_tables_handles_invalid_id_conversion(self, mock_glob, mock_file, mock_dbms):
        """Test import_tables handles non-numeric IDs gracefully."""
        # Arrange
        loader = DBLoader()
        mock_csv_file = MagicMock()
        mock_csv_file.stem = "dishes"
        mock_glob.return_value = [mock_csv_file]
        
        loader.cv_dbms.get_table_size.return_value = 0
        loader.cv_dbms.upload_table.return_value = True

        # Act
        loader.import_tables(force_reload=False)

        # Assert
        loader.cv_dbms.upload_table.assert_called_once()
        uploaded_data = loader.cv_dbms.upload_table.call_args[0][2]
        self.assertEqual(uploaded_data[0]["id"], 5)  # First ID is int
        self.assertEqual(uploaded_data[1]["id"], "invalid_id")  # Second kept as string

    @patch('discord_bot.init.db_loader.DBMS')
    @patch('discord_bot.init.db_loader.Path.glob')
    def test_import_tables_skips_populated_tables(self, mock_glob, mock_dbms):
        """Test import_tables skips tables that already have data."""
        # Arrange
        loader = DBLoader()
        mock_csv_file = MagicMock()
        mock_csv_file.stem = "dishes"
        mock_glob.return_value = [mock_csv_file]
        
        loader.cv_dbms.get_table_size.return_value = 100  # Table has data

        # Act
        loader.import_tables(force_reload=False)

        # Assert
        loader.cv_dbms.upload_table.assert_not_called()

    @patch('discord_bot.init.db_loader.DBMS')
    @patch('builtins.open', new_callable=mock_open, read_data='id,dish\n1,Pizza')
    @patch('discord_bot.init.db_loader.Path.glob')
    def test_import_tables_force_reload_overwrites_data(self, mock_glob, mock_file, mock_dbms):
        """Test import_tables with force_reload overwrites existing data."""
        # Arrange
        loader = DBLoader()
        mock_csv_file = MagicMock()
        mock_csv_file.stem = "dishes"
        mock_glob.return_value = [mock_csv_file]
        
        loader.cv_dbms.get_table_size.return_value = 100  # Table has data
        loader.cv_dbms.upload_table.return_value = True

        # Act
        loader.import_tables(force_reload=True)

        # Assert
        loader.cv_dbms.upload_table.assert_called_once()  # Should reload despite existing data

    # ==================== CRITICAL: Discord Tables Initialization ====================

    @patch('discord_bot.init.db_loader.DBMS')
    def test_initialize_discord_tables_creates_empty_tables(self, mock_dbms):
        """Test initialize_discord_tables creates empty tables."""
        # Arrange
        loader = DBLoader()
        loader.discord_dbms.get_table_size.return_value = 0

        # Act
        loader.initialize_discord_tables()

        # Assert
        loader.discord_dbms.connect.assert_called_once()
        # Should create 5 tables
        self.assertEqual(loader.discord_dbms.insert_data.call_count, 5)
        self.assertEqual(loader.discord_dbms.delete_data.call_count, 5)

    @patch('discord_bot.init.db_loader.DBMS')
    def test_initialize_discord_tables_skips_existing_tables(self, mock_dbms):
        """Test initialize_discord_tables skips tables that already exist."""
        # Arrange
        loader = DBLoader()
        loader.discord_dbms.get_table_size.return_value = 10  # Tables exist

        # Act
        loader.initialize_discord_tables()

        # Assert
        # Should not insert/delete for existing tables
        self.assertEqual(loader.discord_dbms.insert_data.call_count, 0)
        self.assertEqual(loader.discord_dbms.delete_data.call_count, 0)

    @patch('discord_bot.init.db_loader.DBMS')
    @patch('discord_bot.init.db_loader.datetime')
    def test_initialize_discord_tables_creates_statistics_document(self, mock_datetime, mock_dbms):
        """Test initialize_discord_tables creates initial statistics document."""
        # Arrange
        loader = DBLoader()
        loader.discord_dbms.get_table_size.return_value = 0
        loader.discord_dbms.get_data.return_value = []  # No existing stats
        
        mock_date = MagicMock()
        mock_date.date().isoformat.return_value = "2026-01-09"
        mock_datetime.now.return_value = mock_date

        # Act
        loader.initialize_discord_tables()

        # Assert
        # Should insert initial stats (6 = 5 tables + 1 stats)
        self.assertEqual(loader.discord_dbms.insert_data.call_count, 6)
        
        # Check last insert_data call was for statistics
        last_call_args = loader.discord_dbms.insert_data.call_args_list[-1]
        self.assertEqual(last_call_args[0][0], "statistics")
        stats_data = last_call_args[0][1]
        self.assertEqual(stats_data["date"], "2026-01-09")
        self.assertEqual(stats_data["total_messages"], 0)

    @patch('discord_bot.init.db_loader.DBMS')
    @patch('discord_bot.init.db_loader.datetime')
    def test_initialize_discord_tables_skips_existing_statistics(self, mock_datetime, mock_dbms):
        """Test initialize_discord_tables doesn't recreate existing statistics."""
        # Arrange
        loader = DBLoader()
        loader.discord_dbms.get_table_size.return_value = 0
        loader.discord_dbms.get_data.return_value = [{"date": "2026-01-09", "total_messages": 50}]  # Stats exist
        
        mock_date = MagicMock()
        mock_date.date().isoformat.return_value = "2026-01-09"
        mock_datetime.now.return_value = mock_date

        # Act
        loader.initialize_discord_tables()

        # Assert
        # Should insert 5 tables but NOT statistics
        self.assertEqual(loader.discord_dbms.insert_data.call_count, 5)


if __name__ == "__main__":
    unittest.main()
