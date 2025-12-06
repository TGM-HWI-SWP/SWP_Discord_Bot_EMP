"""Discord bot entry point - runs only the Discord bot without Gradio."""
import discord
import runpy

from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.translator import Translator
from discord_bot.business_logic.discord_logic import DiscordLogic
from discord_bot.init.config_loader import DBConfigLoader


def start_bot():
    """Initialize and start the Discord bot."""
    try:
        print("[BOT] Starting Discord bot initialization...", flush=True)
        cv_db = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
        cv_db.connect()
        print("[BOT] CV database connected", flush=True)

        fun_fact_selector = FunFactSelector(dbms=cv_db)
        dish_selector = DishSelector(dbms=cv_db)

        discord_db = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
        discord_db.connect()
        print("[BOT] Discord database connected", flush=True)

        translator = Translator(dbms=discord_db)
        discord_bot = DiscordLogic(dbms=discord_db)
        print("[BOT] Discord bot instance created", flush=True)

        async def funfact_command(interaction: discord.Interaction):
            await interaction.response.send_message(fun_fact_selector.execute_function())

        async def dish_command(interaction: discord.Interaction, category: str):
            await interaction.response.send_message(dish_selector.execute_function(category))

        async def translate_command(interaction: discord.Interaction):
            await interaction.response.send_message(translator.execute_function())

        async def auto_translate_command(interaction: discord.Interaction):
            await interaction.response.send_message(translator.execute_function())
        
        discord_bot.register_command("funfact", funfact_command, description="Get a random fun fact")
        discord_bot.register_command("dish", dish_command, description="Get a dish suggestion")
        discord_bot.register_command("translate", translate_command, description="Translate message to target language")
        discord_bot.register_command("auto-translate", auto_translate_command, description="Auto-translate message to target language based on user_id")
        print("[BOT] Commands registered, calling bot.run()...", flush=True)

        discord_bot.run()
    except Exception as e:
        print(f"[BOT] Exception in bot thread: {e}", flush=True)
    

if __name__ == "__main__":
    print("=== Running initialization (Discord Bot Only) ===", flush=True)

    try:
        runpy.run_module('discord_bot.init.log_loader', run_name='__main__')
        print("[INIT] Log loader complete", flush=True)
    except Exception as e:
        print(f"[INIT] Log loader failed: {e}", flush=True)
    
    try:
        runpy.run_module('discord_bot.init.db_loader', run_name='__main__')
        print("[INIT] DB loader complete", flush=True)
    except Exception as e:
        print(f"[INIT] DB loader failed: {e}", flush=True)
    
    print("=== Starting Discord Bot ===", flush=True)
    start_bot()
