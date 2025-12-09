import discord
import threading
import time
import runpy
import uuid

from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.translator import Translator
from discord_bot.business_logic.discord_logic import DiscordLogic
from discord_bot.init.config_loader import DBConfigLoader
from discord_bot.adapters.view import AdminPanel


# ALL OF THE [xxx] ARE LOGGING MESSAGES AND NEED TO BE REMOVED AFTER TESTING ALSO UUID SHOULD BE REMOVED
def start_bot(startup_id: str):
    import threading as th
    thread_id = th.get_ident()
    try:
        print(f"[BOT] [{startup_id}] [Thread-{thread_id}] Starting Discord bot initialization...", flush=True)
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
            await interaction.response.send_message(translator.execute_function()) # also needs text to be passed on execution from command parameter

        async def auto_translate_command(interaction: discord.Interaction):
            await interaction.response.send_message(translator.execute_function()) # also needs text to be passed on execution from command parameter and auto-translate target to be passed
        
        discord_bot.register_command("funfact", funfact_command, description="Get a random fun fact")
        discord_bot.register_command("dish", dish_command, description="Get a dish suggestion")
        discord_bot.register_command("translate", translate_command, description="Translate message to target language")
        discord_bot.register_command("auto-translate", auto_translate_command, description="Auto-translate message to target language based on user_id")
        print("[BOT] Commands registered, calling bot.run()...", flush=True)

        discord_bot.run()
    except Exception as e:
        print(f"[BOT] Exception in bot thread: {e}", flush=True)
    
if __name__ == "__main__":
    # TESTING: Unique startup ID to verify single execution
    STARTUP_ID = str(uuid.uuid4())[:8]
    print(f"[STARTUP_ID] {STARTUP_ID} - Application starting", flush=True)
    print("=== Running initialization ===", flush=True)

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
    
    main_thread_id = threading.get_ident()
    print(f"[STARTUP_ID] {STARTUP_ID} - Starting application [MainThread-{main_thread_id}]", flush=True)
    print("=== Starting application ===", flush=True)
    bot_thread = threading.Thread(target=start_bot, args=(STARTUP_ID,), daemon=False, name="DiscordBot")
    bot_thread.start()
    print(f"[MAIN] [{STARTUP_ID}] [Thread-{main_thread_id}] Discord bot thread started, waiting 2 seconds...", flush=True)
    time.sleep(2)
    
    print(f"[MAIN] [{STARTUP_ID}] [Thread-{main_thread_id}] Setting up Gradio interface...", flush=True)
    cv_db = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
    cv_db.connect()
    print("[MAIN] CV DB connected", flush=True)
    discord_db = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    discord_db.connect()
    print("[MAIN] Discord DB connected", flush=True)
    
    dish_selector = DishSelector(dbms=cv_db)
    fun_fact_selector = FunFactSelector(dbms=cv_db)
    translator = Translator(dbms=discord_db)
    print("[MAIN] Selectors created", flush=True)
    
    panel = AdminPanel(
        dbms=cv_db,
        dish_selector=dish_selector,
        fun_fact_selector=fun_fact_selector,
        translator=translator
    )
    print("[MAIN] AdminPanel created, launching Gradio (this may take time)...", flush=True)
    panel.launch()
    print("[MAIN] Gradio interface launched", flush=True)
