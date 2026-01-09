"""Unit tests for FunFactSelector class."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import Mock

from discord_bot.business_logic.fun_fact_selector import FunFactSelector


class TestFunFactSelector(unittest.TestCase):
    """Test the FunFactSelector business logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_dbms = Mock()
        self.fun_fact_selector = FunFactSelector(dbms=self.mock_dbms)

    def test_execute_function_returns_fun_fact(self):
        """Test that execute_function returns a fun fact from database."""
        # Arrange
        expected_fact = "Did you know that honey never spoils?"
        self.mock_dbms.get_random_entry.return_value = {"fun_fact": expected_fact}

        # Act
        result = self.fun_fact_selector.execute_function()

        # Assert
        self.assertEqual(result, expected_fact)
        self.mock_dbms.get_random_entry.assert_called_once_with("fun_facts", None)

    def test_execute_function_returns_empty_string_when_no_fact(self):
        """Test that execute_function returns empty string when no fact is found."""
        # Arrange
        self.mock_dbms.get_random_entry.return_value = {}

        # Act
        result = self.fun_fact_selector.execute_function()

        # Assert
        self.assertEqual(result, "")
        self.mock_dbms.get_random_entry.assert_called_once_with("fun_facts", None)

    def test_execute_function_always_queries_with_none_category(self):
        """Test that execute_function always passes None as category."""
        # Arrange
        self.mock_dbms.get_random_entry.return_value = {"fun_fact": "Test fact"}

        # Act
        self.fun_fact_selector.execute_function()

        # Assert
        _, called_category = self.mock_dbms.get_random_entry.call_args[0]
        self.assertIsNone(called_category)

    def test_execute_function_handles_missing_fun_fact_key(self):
        """Test that execute_function handles documents without 'fun_fact' key."""
        # Arrange
        self.mock_dbms.get_random_entry.return_value = {"id": 456, "text": "Some text"}

        # Act
        result = self.fun_fact_selector.execute_function()

        # Assert
        self.assertIn("456", result)  # Falls back to str(fun_fact)

    def test_multiple_calls_query_database_each_time(self):
        """Test that multiple calls to execute_function query the database each time."""
        # Arrange
        facts = [
            {"fun_fact": "Fact 1"},
            {"fun_fact": "Fact 2"},
            {"fun_fact": "Fact 3"},
        ]
        self.mock_dbms.get_random_entry.side_effect = facts

        # Act
        results = [self.fun_fact_selector.execute_function() for _ in range(3)]

        # Assert
        self.assertEqual(len(results), 3)
        self.assertEqual(self.mock_dbms.get_random_entry.call_count, 3)
        self.assertEqual(results, ["Fact 1", "Fact 2", "Fact 3"])


if __name__ == "__main__":
    unittest.main()
