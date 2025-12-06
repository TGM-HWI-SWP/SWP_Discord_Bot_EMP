"""Gradio admin panel entry point - runs only the Gradio interface without Discord bot."""
import runpy

from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.translator import Translator
from discord_bot.init.config_loader import DBConfigLoader
from discord_bot.adapters.view import AdminPanel


def start_gradio():
    """Initialize and start the Gradio admin interface."""
    print("[GRADIO] Setting up Gradio interface...", flush=True)
    
    cv_db = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
    cv_db.connect()
    print("[GRADIO] CV DB connected", flush=True)
    
    discord_db = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    discord_db.connect()
    print("[GRADIO] Discord DB connected", flush=True)
    
    dish_selector = DishSelector(dbms=cv_db)
    fun_fact_selector = FunFactSelector(dbms=cv_db)
    translator = Translator(dbms=discord_db)
    print("[GRADIO] Selectors created", flush=True)
    
    panel = AdminPanel(
        dbms=cv_db,
        dish_selector=dish_selector,
        fun_fact_selector=fun_fact_selector,
        translator=translator
    )
    print("[GRADIO] AdminPanel created, launching Gradio...", flush=True)
    panel.launch()
    print("[GRADIO] Gradio interface launched", flush=True)


if __name__ == "__main__":
    print("=== Running initialization (Gradio Only) ===", flush=True)

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
    
    print("=== Starting Gradio Interface ===", flush=True)
    start_gradio()
