"""Provide a base model class with logging support."""

from datetime import datetime

from discord_bot.contracts.ports import ModelPort
from discord_bot.init.log_loader import LogLoader


class Model(ModelPort):
    def __init__(self) -> None:
        self.log_loader = LogLoader()

    def logging(self, message: str = "Model logging", log_file_name: str | None = None) -> None:
        try:
            if log_file_name:
                log_file = self.log_loader.get_log_file_path(log_file_name, treat_as_filename=True)
            else:
                class_name = self.__class__.__name__
                log_file = self.log_loader.get_log_file_path(class_name)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_file.parent.mkdir(parents=True, exist_ok=True)
            if not log_file.exists():
                log_file.touch()

            with open(log_file, "a", encoding="utf-8") as file:
                file.write(f'[{timestamp}] {message}\n')

        except Exception as error:
            print(f'Logging failed: {error}')
