from datetime import datetime

from discord_bot.contracts.ports import ModelPort
from discord_bot.init.log_loader import LogLoader

class Model(ModelPort):
    def __init__(self):
        self.log_loader = LogLoader()

    def logging(self, message: str = "Model logging") -> None:
        try:
            class_name = self.__class__.__name__
            log_file = self.log_loader.get_log_file_path(class_name)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(log_file, "a", encoding="utf-8") as file:
                file.write(f'[{timestamp}] {message}\n')

        except Exception as error:
            print(f'Logging failed: {error}')
