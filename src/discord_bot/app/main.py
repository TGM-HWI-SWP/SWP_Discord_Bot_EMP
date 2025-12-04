import discord

from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.translator import Translator
from discord_bot.business_logic.discord_logic import DiscordLogic
from discord_bot.init.config_loader import DBConfigLoader

if __name__ == "__main__":
    cv_db = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
    cv_db.connect()

    # TESTING FUN FACT SELECTOR
    fun_fact_selector = FunFactSelector(dbms=cv_db)
    print("=== FUN FACT TEST ===")
    print(fun_fact_selector.execute_function())

    # TESTING DISH SELECTOR
    dish_selector = DishSelector(dbms=cv_db)
    print("=== DISH SUGGESTION TEST ===")
    print(dish_selector.execute_function(category="Italian"))

    # TESTING TRANSLATOR
    translator = Translator()
    sample_text = "Merhaba, nasılsın?"
    translated_text = translator.execute_function(sample_text)
    print("=== TRANSLATION TEST ===")
    print(f"Original: {sample_text}")
    print(f"Translated: {translated_text}")

    # TESTING DISCORD BOT CONNECTION
    print("=== DISCORD BOT TEST ===")
    discord_db = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    discord_db.connect()
    discord_bot = DiscordLogic(dbms=discord_db)
    async def test_command(interaction: discord.Interaction):
        await interaction.response.send_message("Hello World!")
    discord_bot.register_command("test", test_command, description="Test command to verify bot functionality")
    print("Discord bot starting... Press Ctrl+C to stop.")
    discord_bot.run()
