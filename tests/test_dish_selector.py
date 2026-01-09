"""Unit tests for DishSelector class."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import Mock, MagicMock

from discord_bot.business_logic.dish_selector import DishSelector


class TestDishSelector(unittest.TestCase):
    """Test the DishSelector business logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_dbms = Mock()
        self.dish_selector = DishSelector(dbms=self.mock_dbms)

    def test_execute_function_returns_dish_name(self):
        """Test that execute_function returns the dish name from database."""
        # Arrange
        expected_dish = "Pizza Margherita"
        self.mock_dbms.get_random_entry.return_value = {"dish": expected_dish, "category": "Italian"}

        # Act
        result = self.dish_selector.execute_function("Italian")

        # Assert
        self.assertEqual(result, expected_dish)
        self.mock_dbms.get_random_entry.assert_called_once_with("dishes", "Italian")

    def test_execute_function_returns_empty_string_when_no_dish(self):
        """Test that execute_function returns empty string when no dish is found."""
        # Arrange
        self.mock_dbms.get_random_entry.return_value = {}

        # Act
        result = self.dish_selector.execute_function("NonExistentCategory")

        # Assert
        self.assertEqual(result, "")
        self.mock_dbms.get_random_entry.assert_called_once_with("dishes", "NonExistentCategory")

    def test_execute_function_with_different_categories(self):
        """Test that execute_function works with different categories."""
        # Arrange
        test_cases = [
            ("Italian", {"dish": "Spaghetti Carbonara"}),
            ("Chinese", {"dish": "Sweet and Sour Chicken"}),
            ("Mexican", {"dish": "Tacos"}),
        ]

        for category, mock_data in test_cases:
            with self.subTest(category=category):
                self.mock_dbms.get_random_entry.return_value = mock_data

                # Act
                result = self.dish_selector.execute_function(category)

                # Assert
                self.assertEqual(result, mock_data["dish"])

    def test_execute_function_handles_missing_dish_key(self):
        """Test that execute_function handles documents without 'dish' key."""
        # Arrange
        self.mock_dbms.get_random_entry.return_value = {"id": 123, "category": "Italian"}

        # Act
        result = self.dish_selector.execute_function("Italian")

        # Assert
        self.assertIn("123", result)  # Falls back to str(dish)

    def test_dbms_integration(self):
        """Test that DishSelector correctly uses the dbms instance."""
        # Arrange & Act
        selector = DishSelector(dbms=self.mock_dbms)

        # Assert
        self.assertIs(selector.dbms, self.mock_dbms)


if __name__ == "__main__":
    unittest.main()
