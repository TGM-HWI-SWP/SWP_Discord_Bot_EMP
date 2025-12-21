"""Define abstract base classes (ports) for the Discord bot architecture."""

from abc import ABC, abstractmethod
from typing import overload

class DatabasePort(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    def connect(self, max_attempts: int = 10, delay_seconds: float = 2) -> None:
        """Connect to the database.

        Args:
            max_attempts (int): Maximum number of connection attempts.
            delay_seconds (float): Delay in seconds between attempts.

        Raises:
            ConnectionFailure: If the database connection fails after all attempts.
        """
        ...

    @abstractmethod
    def get_data(self, table_name: str, query: dict) -> list[dict]:
        """Fetch data from a table based on a query.

        Args:
            table_name (str): Name of the table to fetch data from.
            query (dict): Query parameters to filter the data.

        Returns:
            List of dictionaries representing the fetched rows.

        Raises:
            RuntimeError: If the database connection is not available.
        """
        ...

    @abstractmethod
    def get_distinct_values(self, table_name: str, field: str) -> list[str]:
        """Get distinct values for a field in a table.

        Args:
            table_name (str): Name of the table to query.
            field (str): Field whose distinct values should be returned.

        Returns:
            Sorted list of distinct, non-null values.

        Raises:
            RuntimeError: If the database connection is not available.
        """
        ...
    
    @abstractmethod
    def insert_data(self, table_name: str, data: dict) -> bool:
        """Insert a single document into a table.

        Args:
            table_name (str): Name of the table to insert data into.
            data (dict): Mapping representing the row to insert.

        Returns:
            True if the insertion was acknowledged, otherwise False.

        Raises:
            RuntimeError: If the database connection is not available.
        """
        ...
    
    @abstractmethod
    def update_data(self, table_name: str, query: dict, data: dict) -> bool:
        """Update one or more rows in a table.

        Args:
            table_name (str): Name of the table to update.
            query (dict): Filter specifying which rows to update.
            data (dict): Fields to set on the matched rows.

        Returns:
            True if the update was acknowledged, otherwise False.

        Raises:
            RuntimeError: If the database connection is not available.
        """
        ...

    @abstractmethod
    def delete_data(self, db_name: str, query: dict) -> bool:
        """Delete rows from a table based on a query.

        Args:
            db_name (str): Name of the database containing the table to delete data from.
            query (dict): Filter specifying which rows to delete.

        Returns:
            True if the deletion was acknowledged, otherwise False.

        Raises:
            RuntimeError: If the database connection is not available.
        """
        ...

    @abstractmethod
    def get_random_entry(self, table_name: str, category: str | None) -> dict:
        """Fetch a random entry from a table.

        Args:
            table_name (str): Name of the table to fetch data from.
            category (str | None): Optional category to filter the rows.

        Returns:
            Dictionary representing the random entry, or an empty dict.

        Raises:
            RuntimeError: If the database connection is not available.
        """
        ...
    
    @abstractmethod
    def get_table_size(self, table_name: str, category: str | None = None) -> int:
        """Get the number of rows in a table.

        Args:
            table_name (str): Name of the table.
            category (str | None): Optional category to filter by.

        Returns:
            Number of entries in the table (or in the given category).

        Raises:
            RuntimeError: If the database connection is not available.
        """
        ...

    @abstractmethod
    def upload_table(self, db_name: str, table_name: str, data: list[dict], drop_existing: bool = True) -> bool:
        """Bulk-upload a list of documents to a target database table.

        Args:
            db_name (str): Name of the target database.
            table_name (str): Name of the target table.
            data (list[dict]): Documents to insert.
            drop_existing (bool): Whether to drop the existing collection first.

        Returns:
            bool: True if any documents were inserted, otherwise False.

        Raises:
            RuntimeError: If the upload fails for any reason.
        """
        ...

class ModelPort(ABC):
    """Abstract interface for basic model behaviour."""

    @abstractmethod
    def logging(self, message: str = "Model logging", log_file_name: str | None = None) -> None:
        """Write a log message for the current model.

        Args:
            message (str): Message to log.
            log_file_name (str | None): Optional explicit log file name; if omitted, the class name is used.
        """
        ...

    @abstractmethod
    def execute_function(self, *args, **kwargs):
        """Execute the primary domain-specific function of the model."""
        ...

class TranslatePort(ModelPort):
    """Abstract interface for translation models."""
    @overload
    def execute_function(self, text: str) -> str:
        """Translate a single message.

        Args:
            text (str): Text to translate.

        Returns:
            Translated message.
        """
        ...
    
    @overload
    def execute_function(self, text: str, user_id: int) -> str:
        """Auto-translate using a user's preferred language.

        Args:
            text (str): Text to translate.
            user_id (int): User ID whose language preference should be used.

        Returns:
            Translated message.
        """
        ...

class FunFactPort(ModelPort):
    """Abstract interface for fun-fact providers."""

    @abstractmethod
    def execute_function(self) -> str:
        """Return a random fun fact.

        Returns:
            str: Random fun fact as a string.
        """
        ...

class DishPort(ModelPort):
    """Abstract interface for dish suggestion providers."""

    @abstractmethod
    def execute_function(self, category: str) -> str:
        """Suggest a dish for a specific category.

        Args:
            category (str): Category of the dish to suggest.

        Returns:
            Suggested dish name.
        """
        ...

class ControllerPort(ABC):
    """Abstract interface for a high-level application controller."""

    @abstractmethod
    def get_fun_fact(self) -> str:
        """Return a random fun fact.

        Returns:
            str: Random fun fact as a string.
        """
        ...

    @abstractmethod
    def get_dish_suggestion(self, category: str) -> str:
        """Get a dish suggestion for a specific category.

        Args:
            category (str): Category of dish to suggest.

        Returns:
            Suggested dish name.
        """
        ...

    @abstractmethod
    def translate_text(self, text: str) -> str:
        """Translate text to the target language.

        Args:
            text (str): Text to translate.

        Returns:
            Translated text.
        """
        ...

class ViewPort(ABC):
    """Abstract interface for UI view adapters."""

    @abstractmethod
    def get_user_input(self, interactable_element: str) -> str:
        """Get user input from the specified interactable element.

        Args:
            interactable_element (str): The interactable element to get input from.

        Returns:
            User input as a string.
        """
        ...

    @abstractmethod
    def check_available(self) -> bool:
        """Check if the Discord Bot is available.

        Returns:
            bool: True if the Discord Bot is available, False otherwise.
        """
        ...

    @abstractmethod
    def check_connection(self) -> bool:
        """Check if the Discord Bot is connected and available.

        Returns:
            bool: True if connected, False otherwise.
        """
        ...

    @abstractmethod
    def build_interface(self):
        """Build and return the view's UI components."""
        ...

    @abstractmethod
    def launch(self, share: bool = False) -> None:
        """Launch the view/UI server.

        Args:
            share (bool): Whether to expose the UI publicly using Gradio's share feature.
        """
        ...

class DiscordLogicPort(ABC):
    """Abstract interface for Discord bot logic and integration."""
    
    @abstractmethod
    def send_message(self, guild_id: int, channel_id: int, message: str) -> bool:
        """Send a message to the specified Discord guild and channel.

        Args:
            guild_id (int): ID of the Discord guild.
            channel_id (int): ID of the channel to send the message to.
            message (str): Message to be sent.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        ...

    @abstractmethod
    def run(self) -> None:
        """Start the Discord bot and connect to Discord guilds.
        
        This method should be called to initialize the bot connection and start
        listening for events and commands.
        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """Gracefully stop the Discord bot and close the client connection."""

    @abstractmethod
    def get_guilds(self) -> list[dict]:
        """Get information about all guilds the bot is connected to.

        Returns:
            list[dict]: A list of dictionaries containing guild information.
                Each dictionary should include at least 'id' and 'name' keys.
        """
        ...
    
    @abstractmethod
    def get_guild_info(self, guild_id: int) -> dict | None:
        """Get information about a specific guild.

        Args:
            guild_id (int): ID of the Discord guild.

        Returns:
            dict | None: A dictionary containing guild information including 'id', 'name', and 'member_count',
                or None if the guild is not found.
        """
        ...
    
    @abstractmethod
    def leave_guild(self, guild_id: int) -> bool:
        """Make the bot leave a specific guild.

        Args:
            guild_id (int): ID of the Discord guild to leave.

        Returns:
            bool: True if the bot successfully left the guild, False otherwise.
        """
        ...
    
    @abstractmethod
    def update_settings(self, prefix: str, status_text: str, auto_reply: bool, log_messages: bool) -> bool:
        """Update the bot's settings.

        Args:
            prefix (str): Command prefix to set.
            status_text (str): Status text to display.
            auto_reply (bool): Whether to enable auto-reply.
            log_messages (bool): Whether to log messages.

        Returns:
            bool: True if settings were updated successfully, False otherwise.
        """
        ...
    
    @abstractmethod
    def get_bot_stats(self) -> dict:
        """Get bot statistics: status, guild count, and total user count.

        Returns:
            dict: A dictionary containing 'status', 'guilds', and 'users' keys.
        """
        ...

    @abstractmethod
    def get_channels(self, guild_id: int) -> list[dict]:
        """Get all channels for a specific guild.

        Args:
            guild_id (int): ID of the Discord guild.

        Returns:
            list[dict]: A list of dictionaries containing channel information.
                Each dictionary should include at least 'id' and 'name' keys.
        """
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the bot is currently connected to Discord.

        Returns:
            bool: True if the bot is connected, False otherwise.
        """
        ...

    @abstractmethod
    def set_translator(self, translator: TranslatePort) -> None:
        """Attach a translator implementation to the Discord logic.

        Args:
            translator (TranslatePort): Translator to use for auto-translation.
        """
        ...

    @abstractmethod
    def get_unread_dms(self) -> list[dict]:
        """Get a list of unread direct messages (DMs).

        Returns:
            list[dict]: A list of dictionaries representing unread DMs.
        """
        ...

    @abstractmethod
    def mark_dm_as_read(self, dm_id: int) -> bool:
        """Mark a specific DM as read.

        Args:
            dm_id (int): Message ID of the DM to mark read.

        Returns:
            bool: True if a DM was found and marked.
        """
        ...

    @abstractmethod
    def mark_all_dms_as_read(self) -> int:
        """Mark all unread DMs as read and return the count updated.

        Returns:
            int: Number of DMs that were marked as read.
        """
        ...

    @abstractmethod
    def enable_auto_translate(self, target_user_id: int, subscriber_user_id: int, target_user_name: str | None = None, subscriber_user_name: str | None = None) -> None:
        """Enable auto-translation from a target user to a subscriber.

        Args:
            target_user_id (int): ID of the user whose messages will be translated.
            subscriber_user_id (int): ID of the user receiving translations.
            target_user_name (str | None): Optional target display name.
            subscriber_user_name (str | None): Optional subscriber display name.
        """
        ...

    @abstractmethod
    def disable_auto_translate(self, target_user_id: int, subscriber_user_id: int) -> None:
        """Disable auto-translation for the given target/subscriber pair.

        Args:
            target_user_id (int): ID of the target user.
            subscriber_user_id (int): ID of the subscriber.
        """
        ...

    @abstractmethod
    def register_command(self, command: str, callback: callable, description: str = "", option_name: str | None = None, choices: list[str] | None = None) -> bool:
        """Register a slash command with optional parameters.

        Args:
            command (str): Command name (without prefix, e.g., 'funfact').
            callback (callable): Async function to call when the command is invoked.
            description (str): Description of the command.
            option_name (str | None): Name of the option (for dropdown menu).
            choices (list[str] | None): Choices of the option (for dropdown menu).

        Returns:
            bool: True if the command was registered successfully, False otherwise.
        """
        ...

    @abstractmethod
    async def on_message(self, message) -> None:
        """Handle incoming Discord messages.

        Args:
            message: The Discord message object.
        """
        ...
