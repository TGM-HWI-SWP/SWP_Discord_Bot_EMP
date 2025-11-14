"""This module defines abstract base classes (ports) for various components of the Discord bot architecture."""

from abc import ABC, abstractmethod

class DatabasePort(ABC):
    @abstractmethod
    def get_data(self, table: str, query: dict) -> list[dict]: # what does list do
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

class ModelPort(ABC):
    @abstractmethod
    def logging(self):
        ...

    @abstractmethod
    def execute_function(self): # multiple dispatch
        ...

class TranslatePort(ABC, ModelPort):
    @abstractmethod
    def execute_function(self, message_id: int, target_language: str) -> str: # use for auto translate to? add param
        """Translate the message with the given ID to the target language.

        Args:
            message_id (int): The ID of the message to be translated.
            target_language (str): The language to translate the message into.

        Returns:
            str: The translated message.
        """
        ...

class FunFactPort(ABC, ModelPort):
    @abstractmethod
    def execute_function() -> str:
        """Fetch a fun fact from the specified category.

        Returns:
            str: A fun fact.
        """
        ...

class DishPort(ABC, ModelPort):
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
    def handle_command(self, server_id: int, channel_id: int, command: str, args: list[str]) -> bool:
        """Handle a command issued in the Discord server.

        Args:
            server_id (int): The ID of the Discord server.
            channel_id (int): The ID of the channel where the command was issued.
            command (str): The command to be handled.
            args (list[str]): The arguments provided with the command.

        Returns:
            bool: True if the command was handled successfully, False otherwise.
        """
        ...

    @abstractmethod
    def handle_message(self, server_id: int, channel_id: int, message: str) -> bool:
        """Handle a message sent in the Discord server.

        Args:
            server_id (int): The ID of the Discord server.
            channel_id (int): The ID of the channel where the message was sent.
            message (str): The message to be handled.

        Returns:
            bool: True if the message was handled successfully, False otherwise.
        """
        ...

    @abstractmethod
    def get_server_info() -> list[dict]:
        """Fetch information about the Discord servers the bot is connected to.

        Returns:
            list[dict]: A list of dictionaries representing the server information.
        """
        ...

class ViewPort(ABC):
    @abstractmethod
    def render_interface(self, data: dict) -> str:
        """Render the user interface based on the provided data.

        Args:
            data (dict): The data to be used for rendering the interface.

        Returns:
            str: The rendered interface as a string.
        """
        ...

    @abstractmethod
    def get_user_input(self, interactable_element: str) -> str:
        """Get user input from the specified interactable element.

        Args:
            interactable_element (str): The interactable element to get input from.

        Returns:
            str: The user input as a string.
        """
        ...
