"""This module defines abstract base classes (ports) for various components of the Discord bot architecture."""

from abc import ABC, abstractmethod
from typing import overload

class DatabasePort(ABC):
    @abstractmethod
    def connect(self, max_attempts: int = 10, delay_seconds: float = 2) -> None:
        """Connect to the database.

        Args:
            max_attempts (int): The maximum number of attempts to connect to the database.
            delay_seconds (float): The delay in seconds between attempts.

        Raises:
            ConnectionFailure: If the database connection fails after the maximum number of attempts.
        """
        ...

    @abstractmethod
    def get_data(self, table: str, query: dict) -> list[dict]:
        """Fetch data from the specified table based on the query.

        Args:
            table (str): The name of the table to fetch data from.
            query (dict): The query parameters to filter the data.

        Returns:
            list[dict]: A list of dictionaries representing the fetched data.
        """
        ...
    
    @abstractmethod
    def insert_data(self, table: str, data: dict) -> bool:
        """Insert data into the specified table.

        Args:
            table (str): The name of the table to insert data into.
            data (dict): The data to be inserted.

        Returns:
            bool: True if the insertion was successful, False otherwise.
        """
        ...
    
    @abstractmethod
    def update_data(self, table: str, query: dict, data: dict) -> bool:
        """Update data in the specified table based on the query.

        Args:
            table (str): The name of the table to update data in.
            query (dict): The query parameters to filter the data to be updated.
            data (dict): The new data to be updated.
        
        Returns:
            bool: True if the update was successful, False otherwise.
        """
        ...

    @abstractmethod
    def delete_data(self, table: str, query: dict) -> bool:
        """Delete data from the specified table based on the query.

        Args:
            table (str): The name of the table to delete data from.
            query (dict): The query parameters to filter the data to be deleted.
        
        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        ...

    @abstractmethod
    def get_random_entry(self, table: str, category: str | None) -> dict:
        """Fetch a random entry from the specified table and category.

        Args:
            table (str): The name of the table to fetch data from.
            category (str): The category to filter the data (optional).
            
        Returns:
            dict: A dictionary representing the random entry.
        """
        ...
    
    @abstractmethod
    def get_table_size(self, table: str, category: str | None = None) -> int:
        """Get the size of the specified table, optionally filtered by category.

        Args:
            table (str): The name of the table.
            category (str | None): The category to filter by. If None, count all entries.

        Returns:
            int: The number of entries in the table (or in the specified category).
        """
        ...

class ModelPort(ABC):
    @abstractmethod
    def logging(self):
        """Log model activities and interactions."""
        ...

    @abstractmethod
    def execute_function(self):
        """Execute the primary function of the model."""
        ...

class TranslatePort(ModelPort):
    @overload
    def execute_function(self, text: str) -> str:
        """Single-message translation.
        
        Args:
            text (str): The text to translate.
        
        Returns:
            str: The translated message.
        """
        ...
    
    @overload
    def execute_function(self, text: str, user_id: int) -> str:
        """Auto-translate message using user's preferred language.
        
        Args:
            text (str): The text to translate.
            user_id (int): The user ID to look up language preference.
        
        Returns:
            str: The translated message.
        """
        ...
    

class FunFactPort(ModelPort):
    @abstractmethod
    def execute_function(self) -> str:
        """Fetch a fun fact from the specified category.

        Returns:
            str: A fun fact.
        """
        ...

class DishPort(ModelPort):
    @abstractmethod
    def execute_function(self, category: str) -> str:
        """Suggest a dish based on the provided ingredients.

        Args:
            category (str): The category of the dish to suggest.
            
        Returns:
            str: A suggested dish.
        """
        ...

class ControllerPort(ABC):
    @abstractmethod
    def get_fun_fact(self) -> str:
        """Get a random fun fact.

        Returns:
            str: A random fun fact.
        """
        ...

    @abstractmethod
    def get_dish_suggestion(self, category: str) -> str:
        """Get a dish suggestion for a specific category.

        Args:
            category (str): The category of dish to suggest.

        Returns:
            str: A suggested dish name.
        """
        ...

    @abstractmethod
    def translate_text(self, text: str) -> str:
        """Translate text to the target language.

        Args:
            text (str): The text to translate.

        Returns:
            str: The translated text.
        """
        ...

class ViewPort(ABC):
    @abstractmethod
    def get_user_input(self, interactable_element: str) -> str:
        """Get user input from the specified interactable element.

        Args:
            interactable_element (str): The interactable element to get input from.

        Returns:
            str: The user input as a string.
        """
        ...

class DiscordLogicPort(ABC):
    @abstractmethod
    def send_message(self, server_id: int, channel_id: int, message: str) -> bool:
        """Send a message to the specified Discord server and channel.

        Args:
            server_id (int): The ID of the Discord server.
            channel_id (int): The ID of the channel to send the message to.
            message (str): The message to be sent.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        ...

    @abstractmethod
    def send_dm(self, user_id: int, message: str) -> bool:
        """Send a direct message to the specified user.

        Args:
            user_id (int): The ID of the user to send the direct message to.
            message (str): The message to be sent.

        Returns:
            bool: True if the direct message was sent successfully, False otherwise.
        """
        ...

    @abstractmethod
    def run(self) -> None:
        """Start the Discord bot and connect to Discord servers.
        
        This method should be called to initialize the bot connection and start
        listening for events and commands.
        """
        ...

    @abstractmethod
    def get_servers(self) -> list[dict]:
        """Get information about all servers the bot is connected to.

        Returns:
            list[dict]: A list of dictionaries containing server information.
                Each dictionary should include at least 'id' and 'name' keys.
        """
        ...

    @abstractmethod
    def get_channels(self, server_id: int) -> list[dict]:
        """Get all channels for a specific server.

        Args:
            server_id (int): The ID of the Discord server.

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
    def register_command(self, command: str, callback: callable) -> bool:
        """Register a command handler for the Discord bot.

        Args:
            command (str): The command name (without prefix, e.g., 'funfact').
            callback (callable): The async function to call when the command is invoked.

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

    @abstractmethod
    async def on_ready(self) -> None:
        """Handle the bot ready event.
        
        Called when the bot has successfully connected to Discord.
        """
        ...
    