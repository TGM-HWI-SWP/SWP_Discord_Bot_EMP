import discord
from discord import app_commands

from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.translator import Translator
from discord_bot.business_logic.discord_logic import DiscordLogic
from discord_bot.init.config_loader import DBConfigLoader, DiscordConfigLoader

if __name__ == "__main__":
    cv_db = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
    cv_db.connect()

    fun_fact_selector = FunFactSelector(dbms=cv_db)
    dish_selector = DishSelector(dbms=cv_db)

    discord_db = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    discord_db.connect()

    translator = Translator(dbms=discord_db)
    discord_bot = DiscordLogic(dbms=discord_db)

    @discord_bot.tree.command(name="funfact", description="Get a random fun fact")
    async def funfact_command(interaction: discord.Interaction):
        await interaction.response.send_message(fun_fact_selector.execute_function())
        discord_bot._update_command_usage("funfact")

    @discord_bot.tree.command(name="dish", description="Get a dish suggestion")
    @app_commands.describe(category="The category of dish to suggest")
    async def dish_command(interaction: discord.Interaction, category: str):
        await interaction.response.send_message(dish_selector.execute_function(category))
        discord_bot._update_command_usage("dish")

    async def translate_command(interaction: discord.Interaction):
        await interaction.response.send_message(translator.execute_function()) # also needs text to be passed on execution from command parameter

    async def auto_translate_command(interaction: discord.Interaction):
        await interaction.response.send_message(translator.execute_function()) # also needs text to be passed on execution from command parameter and auto-translate target to be passed
    
    discord_bot.register_command("funfact", funfact_command, description="Get a random fun fact")
    discord_bot.register_command("dish", dish_command, description="Get a dish suggestion")
    discord_bot.register_command("translate", translate_command, description="Translate message to target language")
    discord_bot.register_command("auto-translate", auto_translate_command, description="Auto-translate message to target language based on user_id")
    
    discord_bot.run()
    