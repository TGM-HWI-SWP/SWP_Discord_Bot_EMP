import logging
from typing import Any

from discord_bot.contracts.ports import ModelPort

class Model(ModelPort):
    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def logging(self, message: str = "Model logging", *args: Any, **kwargs: Any) -> None:
        self.logger.debug(message, *args, **kwargs)
