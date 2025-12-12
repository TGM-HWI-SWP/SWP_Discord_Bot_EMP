import discord
from discord import app_commands
import runpy
import threading

from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.translator import Translator
from discord_bot.business_logic.discord_logic import DiscordLogic
from discord_bot.init.config_loader import DBConfigLoader
from discord_bot.adapters.view import AdminPanel

def start_bot():
    cv_db = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
    cv_db.connect()

    fun_fact_selector = FunFactSelector(dbms=cv_db)
    dish_selector = DishSelector(dbms=cv_db)

    discord_db = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    discord_db.connect()

    translator = Translator(dbms=discord_db)
    discord_bot = DiscordLogic(dbms=discord_db)
    discord_bot.set_translator(translator)

    async def funfact_command(interaction: discord.Interaction):
        await interaction.response.send_message(fun_fact_selector.execute_function())

    async def dish_command(interaction: discord.Interaction, category: str):
        await interaction.response.send_message(dish_selector.execute_function(category))

    async def translate_command(interaction: discord.Interaction, message: discord.Message):
        text_to_translate = message.content

        if not text_to_translate:
            await interaction.response.send_message("This message has no text content to translate.", ephemeral=True)
            return

        translated_text = translator.execute_function(text_to_translate, user_id=interaction.user.id)

        await interaction.response.send_message(f'**Original:** {text_to_translate}\n**Translated:** {translated_text}', ephemeral=True)

    async def auto_translate_command(interaction: discord.Interaction, target: discord.Member):
        discord_bot.enable_auto_translate(target_user_id=target.id, subscriber_user_id=interaction.user.id)
        await interaction.response.send_message(f'Auto-translate enabled for {target.display_name}.', ephemeral=True)
        discord_bot._update_command_usage("auto-translate")

    async def auto_translate_remove_command(interaction: discord.Interaction, target: discord.Member):
        discord_bot.disable_auto_translate(target_user_id=target.id, subscriber_user_id=interaction.user.id)
        await interaction.response.send_message(f'Auto-translate disabled for {target.display_name}.', ephemeral=True)
        discord_bot._update_command_usage("auto-translate-remove")

    dish_categories = cv_db.get_distinct_values("dishes", "category")

    discord_bot.register_command("funfact", funfact_command, description="Get a random fun fact")
    discord_bot.register_command("dish", dish_command, description="Get a dish suggestion based on the category", option_name="category", choices=dish_categories)
    discord_bot.register_command("Translate", translate_command, description="Translate a message", context_menu=True)
    discord_bot.register_command("auto-translate", auto_translate_command, description="Auto-translate a user's messages", user_option=True)
    discord_bot.register_command("auto-translate-remove", auto_translate_remove_command, description="Stop auto-translate for a user", user_option=True)

    discord_bot.run()
    
if __name__ == "__main__":

    runpy.run_module("discord_bot.init.log_loader", run_name="__main__")
    
    runpy.run_module("discord_bot.init.db_loader", run_name="__main__")
    
    cv_db = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
    cv_db.connect()

    discord_db = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    discord_db.connect()
    
    dish_selector = DishSelector(dbms=cv_db)
    fun_fact_selector = FunFactSelector(dbms=cv_db)
    translator = Translator(dbms=discord_db)
    
    panel = AdminPanel(
        dbms=cv_db,
        dish_selector=dish_selector,
        fun_fact_selector=fun_fact_selector,
        translator=translator
    )

    threading.Thread(target=start_bot, daemon=True).start()

    panel.launch()
