"""Entry point for starting the Discord bot and admin panel."""

import discord
import runpy
import threading

from discord_bot.business_logic.fun_fact_selector import FunFactSelector
from discord_bot.business_logic.dish_selector import DishSelector
from discord_bot.adapters.db import DBMS
from discord_bot.business_logic.translator import Translator
from discord_bot.business_logic.discord_logic import DiscordLogic
from discord_bot.init.config_loader import DBConfigLoader
from discord_bot.adapters.view import AdminPanel


def start_bot() -> None:
    """Create database connections, initialize logic, and start the Discord bot."""
    cv_db = DBMS(db_name=DBConfigLoader.CV_DB_NAME)
    cv_db.connect()

    fun_fact_selector = FunFactSelector(dbms=cv_db)
    dish_selector = DishSelector(dbms=cv_db)

    discord_db = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    discord_db.connect()

    translator = Translator(dbms=discord_db)
    discord_bot = DiscordLogic(dbms=discord_db)
    discord_bot.set_translator(translator)

    async def funfact_command(interaction: discord.Interaction) -> None:
        """Handle the `/funfact` command and send a random fun fact response.

        Args:
            interaction (discord.Interaction): Interaction context for the command.
        """
        await interaction.response.send_message(fun_fact_selector.execute_function())

    async def dish_command(interaction: discord.Interaction, category: str) -> None:
        """Handle the `/dish` command and send a dish suggestion.

        Args:
            interaction (discord.Interaction): Interaction context for the command.
            category (str): Dish category chosen by the user.
        """
        await interaction.response.send_message(dish_selector.execute_function(category))

    async def translate_command(interaction: discord.Interaction, message: discord.Message) -> None:
        """Handle the context-menu translate command for a specific message.

        Args:
            interaction (discord.Interaction): Interaction context for the command.
            message (discord.Message): Message object whose content should be translated.
        """
        text_to_translate = (message.content or "").strip()

        if not text_to_translate or text_to_translate.startswith("http"):
            await interaction.response.send_message("This message has no text content to translate.", ephemeral=True)
            return

        translated_text = translator.execute_function(text_to_translate)

        await interaction.response.send_message(f'**Original:** {text_to_translate}\n**Translated:** {translated_text}', ephemeral=True)

    async def auto_translate_command(interaction: discord.Interaction, target: discord.Member) -> None:
        """Enable auto-translation of a member's messages for the current user.

        Args:
            interaction (discord.Interaction): Interaction context for the command.
            target (discord.Member): Member to auto-translate.
        """
        discord_bot.enable_auto_translate(target_user_id=target.id, subscriber_user_id=interaction.user.id, target_user_name=target.display_name, subscriber_user_name=interaction.user.display_name)
        await interaction.response.send_message(f'Auto-translate enabled for <@{target.id}>.')
        discord_bot._update_command_usage("auto-translate")

    async def auto_translate_remove_command(interaction: discord.Interaction, target: discord.Member) -> None:
        """Disable auto-translation previously enabled for a member.

        Args:
            interaction (discord.Interaction): Interaction context for the command.
            target (discord.Member): Member to disable auto-translation for.
        """
        current = discord_bot.auto_translate_targets.get(target.id, set())
        if interaction.user.id not in current:
            await interaction.response.send_message(f'No auto-translate is set up for <@{target.id}>.')
            return

        discord_bot.disable_auto_translate(target_user_id=target.id, subscriber_user_id=interaction.user.id)
        await interaction.response.send_message(f'Auto-translate disabled for <@{target.id}>.')
        discord_bot._update_command_usage("auto-translate-remove")

    async def auto_translate_list_command(interaction: discord.Interaction) -> None:
        """List all configured auto-translate targets in the guild.

        Args:
            interaction (discord.Interaction): Interaction context for the command.
        """
        targets = discord_bot.auto_translate_targets
        if not targets:
            await interaction.response.send_message("No auto-translate targets are configured.")
            return

        target_lines: list[str] = []
        for target_id, subscribers in targets.items():
            subscriber_names: dict[int, str] = {}

            if discord_bot.dbms:
                for sid in subscribers:
                    sub_records = discord_bot.dbms.get_data("auto_translate", {"target_user_id": target_id, "subscriber_user_id": sid})
                    if sub_records:
                        subscriber_names[sid] = sub_records[0].get("subscriber_user_name")

            target_label = f'<@{target_id}>'
            subscriber_labels = [f'<@{sid}>' for sid in subscribers]
            target_lines.append(f'- {target_label}: {", ".join(subscriber_labels)}')

        reply_content = "**Auto-translate targets:**\nTarget: Subscriber\n" + "\n".join(target_lines)
        await interaction.response.send_message(reply_content)
        discord_bot._update_command_usage("auto-translate-list")

    dish_categories = cv_db.get_distinct_values("dishes", "category")

    discord_bot.register_command("funfact", funfact_command, description="Get a random fun fact")
    discord_bot.register_command("dish", dish_command, description="Get a dish suggestion based on the category", option_name="category", choices=dish_categories)
    discord_bot.register_command("Translate", translate_command, description="Translate a message", context_menu=True)
    discord_bot.register_command("auto-translate", auto_translate_command, description="Auto-translate a user's messages and display it in the channel visible to everyone", user_option=True)
    discord_bot.register_command("auto-translate-remove", auto_translate_remove_command, description="Stop auto-translate for a user", user_option=True)
    discord_bot.register_command("auto-translate-list", auto_translate_list_command, description="List current auto-translate targets")

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
