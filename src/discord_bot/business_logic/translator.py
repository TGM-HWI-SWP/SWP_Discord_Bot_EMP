from deep_translator import GoogleTranslator

from discord_bot.contracts.ports import TranslatePort
from discord_bot.business_logic.model import Model
from discord_bot.init.config_loader import DiscordConfig

class Translator(Model, TranslatePort):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute_function(self, text: str) -> str:
        for attempt in range(10):
            try:
                translator = GoogleTranslator(source="auto", target=DiscordConfig.TARGET_LANGUAGE)
                return translator.translate(text)
            except Exception as e:
                print(f"Translation error (attempt {attempt + 1}/10): {e}")
        return text

if __name__ == "__main__":
    translator = Translator()
    sample_text = "Hello, how are you?"
    translated_text = translator.execute_function(sample_text)
    print(f"Original: {sample_text}")
    print(f"Translated: {translated_text}")
    