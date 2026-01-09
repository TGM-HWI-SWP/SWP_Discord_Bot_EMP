"""Unit tests for Translator class."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
from unittest.mock import Mock, patch, MagicMock

from discord_bot.business_logic.translator import Translator


class TestTranslator(unittest.TestCase):
    """Test the Translator business logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_dbms = Mock()
        self.translator = Translator(dbms=self.mock_dbms)

    @patch('discord_bot.business_logic.translator.GoogleTranslator')
    def test_execute_function_translates_text(self, mock_google_translator):
        """Test that execute_function translates text correctly."""
        # Arrange
        mock_translator_instance = MagicMock()
        mock_translator_instance.translate.return_value = "Hallo Welt"
        mock_google_translator.return_value = mock_translator_instance

        # Act
        result = self.translator.execute_function("Hello World")

        # Assert
        self.assertEqual(result, "Hallo Welt")
        mock_translator_instance.translate.assert_called_once_with("Hello World")

    @patch('discord_bot.business_logic.translator.GoogleTranslator')
    def test_execute_function_with_user_specific_language(self, mock_google_translator):
        """Test that execute_function uses user-specific target language."""
        # Arrange
        user_id = 12345
        self.mock_dbms.get_data.return_value = [{"user_id": user_id, "target_language": "fr"}]
        
        mock_translator_instance = MagicMock()
        mock_translator_instance.translate.return_value = "Bonjour le monde"
        mock_google_translator.return_value = mock_translator_instance

        # Act
        result = self.translator.execute_function("Hello World", user_id=user_id)

        # Assert
        self.assertEqual(result, "Bonjour le monde")
        self.mock_dbms.get_data.assert_called_once_with("users", {"user_id": user_id})
        mock_google_translator.assert_called_with(source="auto", target="fr")

    @patch('discord_bot.business_logic.translator.GoogleTranslator')
    def test_execute_function_returns_original_text_on_failure(self, mock_google_translator):
        """Test that execute_function returns original text when translation fails."""
        # Arrange
        original_text = "Hello World"
        mock_google_translator.side_effect = Exception("Translation API error")

        # Act
        result = self.translator.execute_function(original_text)

        # Assert
        self.assertEqual(result, original_text)
        self.assertEqual(mock_google_translator.call_count, 10)  # Should retry 10 times

    @patch('discord_bot.business_logic.translator.GoogleTranslator')
    def test_execute_function_without_user_id(self, mock_google_translator):
        """Test that execute_function works without user_id."""
        # Arrange
        mock_translator_instance = MagicMock()
        mock_translator_instance.translate.return_value = "Hallo"
        mock_google_translator.return_value = mock_translator_instance

        # Act
        result = self.translator.execute_function("Hello")

        # Assert
        self.assertEqual(result, "Hallo")
        self.mock_dbms.get_data.assert_not_called()

    @patch('discord_bot.business_logic.translator.GoogleTranslator')
    def test_execute_function_with_nonexistent_user(self, mock_google_translator):
        """Test that execute_function uses default language for non-existent user."""
        # Arrange
        user_id = 99999
        self.mock_dbms.get_data.return_value = []  # User not found
        
        mock_translator_instance = MagicMock()
        mock_translator_instance.translate.return_value = "Translated"
        mock_google_translator.return_value = mock_translator_instance

        # Act
        result = self.translator.execute_function("Test", user_id=user_id)

        # Assert
        self.assertEqual(result, "Translated")
        self.mock_dbms.get_data.assert_called_once_with("users", {"user_id": user_id})


if __name__ == "__main__":
    unittest.main()
