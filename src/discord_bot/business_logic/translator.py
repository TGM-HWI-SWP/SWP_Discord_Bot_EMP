"""Business-logic wrapper around `deep_translator` for Discord messages."""

from deep_translator import GoogleTranslator

from discord_bot.contracts.ports import TranslatePort, DatabasePort
from discord_bot.business_logic.model import Model
from discord_bot.init.config_loader import DiscordConfigLoader

class Translator(Model, TranslatePort):
    """Translate text using Google Translate with optional user-specific target languages."""
    def __init__(self, dbms: DatabasePort | None = None, **kwargs):
        super().__init__(**kwargs)
        self.dbms = dbms

    def execute_function(self, text: str, user_id: int | None = None) -> str:
        target_language = DiscordConfigLoader.TARGET_LANGUAGE
        
        if user_id and self.dbms:
            user_data = self.dbms.get_data("users", {"user_id": user_id})
            if user_data:
                # Prefer the user's saved target language.
                target_language = user_data[0].get("target_language", target_language)
        
        for attempt in range(10):
            try:
                translator = GoogleTranslator(source="auto", target=target_language)
                result = translator.translate(text)
                if user_id:
                    self.logging(f'Successfully auto-translated: \'{text}\' -> \'{result}\' (target: {target_language})')
                else:
                    self.logging(f'Successfully translated: \'{text}\' -> \'{result}\' (target: {target_language})')
                return result
            
            except Exception as error:
                self.logging(f'Translation error (attempt {attempt + 1}/10): {error}')
        
        self.logging(f'Translation failed after 10 attempts, returning original text: \'{text}\'')
        return text

if __name__ == "__main__":
    translator = Translator()
    sample_text = "Hello, how are you?"
    translated_text = translator.execute_function(sample_text)
    print(f'Original: {sample_text}')
    print(f'Translated: {translated_text}')
    