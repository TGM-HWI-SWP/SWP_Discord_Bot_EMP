"""Concrete implementation of `DiscordLogicPort` using `discord.py`."""

import asyncio
from datetime import datetime
import discord
from discord import app_commands

from discord_bot.contracts.ports import DiscordLogicPort, DatabasePort, TranslatePort
from discord_bot.init.config_loader import DiscordConfigLoader
from discord_bot.business_logic.model import Model

class DiscordLogic(Model, DiscordLogicPort):
    def __init__(self, dbms: DatabasePort | None = None):
        super().__init__()
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        self.client = discord.Client(intents=intents)
        self.tree = app_commands.CommandTree(self.client)
        self.loop = None
        self.guild_count = 0
        self.commands = {}
        self.unread_dms = []
        self.dbms = dbms
        self.translator: TranslatePort | None = None
        self.auto_translate_targets: dict[int, set[int]] = {}
        if self.dbms:
            self._load_auto_translate_targets()
        
        @self.client.event
        async def on_ready():
            self.loop = asyncio.get_running_loop()
            await self._on_ready()
        
        @self.client.event
        async def on_message(message):
            await self.on_message(message)

        @self.client.event
        async def on_guild_join(guild: discord.Guild):
            self.logging(f'Joined guild: {guild.name} ({guild.id})')
            self._update_connected_guilds()

        @self.client.event
        async def on_guild_remove(guild: discord.Guild):
            self.logging(f'Left guild: {guild.name} ({guild.id})')
            self._update_connected_guilds()

    async def _on_ready(self) -> None:
        """"Handle bot readiness: sync commands and update guild stats."""

        self.logging(f'Logged in as {self.client.user}')
        
        await self.tree.sync()
        self.logging(f'Synced {len(self.tree.get_commands())} slash commands globally')
        
        for guild in self.client.guilds:
            await self.tree.sync(guild=guild)
            self.logging(f'Synced to guild: {guild.name}')

        self._update_connected_guilds()

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.client.user:
            return
        
        if isinstance(message.channel, discord.DMChannel):
            dm_data = {
                "message_id": message.id,
                "user_id": message.author.id,
                "user_name": str(message.author),
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "read": False,
                "is_command": message.content.startswith("/") and message.content in self.commands
            }
            self.unread_dms.append(dm_data)
            self._save_direct_message(dm_data)
        else:
            message_data = {
                "message_id": message.id,
                "guild_id": message.guild.id if message.guild else None,
                "channel_id": message.channel.id,
                "user_id": message.author.id,
                "user_name": str(message.author),
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "is_command": message.content.startswith("/") and message.content in self.commands
            }
            self._save_message(message_data)

        if self.translator and message.author.id in self.auto_translate_targets:
            subscribers = list(self.auto_translate_targets.get(message.author.id, set()))
            text_content = (message.content or "").strip()

            if not text_content or text_content.startswith("http"):
                self.logging(f'Auto-translate skipped for {message.author.display_name}: no translatable text content.', log_file_name="translator")
                return

            for subscriber_id in subscribers:
                translated = self.translator.execute_function(text_content, user_id=subscriber_id)
                try:
                    await message.channel.send(f'**Auto-translate** for <@{subscriber_id}> from <@{message.author.id}>:\n**Translated**: {translated}')
                except Exception as error:
                    self.logging(f'Failed to send auto-translation in channel: {error}', log_file_name="translator")

    def send_message(self, guild_id: int, channel_id: int, message: str) -> bool:
        if not self.client.is_ready() or not self.loop:
            return False

        guild = self.client.get_guild(guild_id)
        if not guild:
            return False

        channel = guild.get_channel(channel_id)
        if not channel:
            return False

        # Schedule the coroutine in the Discord event loop
        future = asyncio.run_coroutine_threadsafe(channel.send(message), self.loop)
        try:
            future.result(timeout=10)  # Block up to 10s for result
            return True
        
        except Exception as error:
            self.logging(f"Failed to send message: {error}")
            return False
    
    def execute_function(self) -> None:
        pass
    
    def run(self) -> None:
        self.logging("Starting Discord bot...")
        token = DiscordConfigLoader.DISCORD_TOKEN

        token_preview = f'{token[:10]}...{token[-4:]}' if len(token) > 14 else "***"
        self.logging(f'Starting Discord bot with token: {token_preview}')
        self.client.run(token)

    def stop(self) -> None:
        asyncio.create_task(self.client.close())

    def set_translator(self, translator: TranslatePort) -> None:
        self.translator = translator
    
    def get_unread_dms(self) -> list[dict]:
        return [dm for dm in self.unread_dms if not dm["read"]]
    
    def mark_dm_as_read(self, dm_id: int) -> bool:
        for dm in self.unread_dms:
            if dm["message_id"] == dm_id and not dm["read"]:
                dm["read"] = True
                return True
        return False
    
    def mark_all_dms_as_read(self) -> int:
        count = sum(1 for dm in self.unread_dms if not dm["read"])
        for dm in self.unread_dms:
            dm["read"] = True
        return count

    def get_guilds(self) -> list[dict]:
        return [{"id": guild.id, "name": guild.name} for guild in self.client.guilds]
    
    def get_guild_info(self, guild_id: int) -> dict | None:
        
        guild = self.client.get_guild(guild_id)
        if guild:
            return {
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count
            }
        return None

    def leave_guild(self, guild_id: int) -> bool:
        if not self.client or not self.client.is_ready():
            return False

        if not self.loop:
            return False

        guild = self.client.get_guild(guild_id)
        if not guild:
            return False

        async def _leave():
            await guild.leave()

        asyncio.run_coroutine_threadsafe(_leave(), self.loop)
        self.logging(f'Leaving guild: {guild_id}')
        return True

    def get_channels(self, guild_id: int) -> list[dict]:
        guild = self.client.get_guild(guild_id)
        if not guild:
            return []
        return [{"id": channel.id, "name": channel.name} for channel in guild.text_channels]

    def is_connected(self) -> bool:
        return self.client.is_ready()
    
    def get_bot_stats(self) -> dict:
        """Get bot statistics: status, guild count, and total user count"""
        if not self.is_connected():
            return {"status": "Offline", "guilds": 0, "users": 0}
        
        try:
            total_members = sum(guild.member_count for guild in self.client.guilds)
            return {
                "status": "Online",
                "guilds": len(self.client.guilds),
                "users": total_members
            }
        except Exception as e:
            self.logging(f"Error getting bot stats: {e}")
            return {"status": "Error", "guilds": 0, "users": 0}

    def update_settings(self, prefix: str, status_text: str, auto_reply: bool, log_messages: bool) -> bool:
        
        if not self.dbms:
            return False
        
        try:
            settings_data = {
                "command_prefix": prefix or "!",
                "status_text": status_text or "Playing",
                "auto_reply": auto_reply,
                "log_messages": log_messages,
                "updated_at": datetime.now().isoformat()
            }

            existing = self.dbms.get_data("settings", {})
            if existing:
                self.dbms.update_data("settings", {}, settings_data)
            else:
                self.dbms.insert_data("settings", settings_data)
                
            self.logging(f'Settings updated: prefix={prefix}, status={status_text}, auto_reply={auto_reply}, log={log_messages}')
            return True
        
        except Exception as error:
            self.logging(f'Error updating settings: {error}')
            return False
        
    def enable_auto_translate(self, target_user_id: int, subscriber_user_id: int, target_user_name: str | None = None, subscriber_user_name: str | None = None) -> None:
        self.auto_translate_targets.setdefault(target_user_id, set()).add(subscriber_user_id)
        if not self.dbms:
            return
        exists = self.dbms.get_data("auto_translate", {"target_user_id": target_user_id, "subscriber_user_id": subscriber_user_id})
        if exists:
            return
        self.dbms.insert_data(
            "auto_translate",
            {
                "target_user_id": target_user_id,
                "subscriber_user_id": subscriber_user_id,
                "target_user_name": target_user_name,
                "subscriber_user_name": subscriber_user_name,
                "created_at": datetime.now().isoformat()
            },
        )

    def disable_auto_translate(self, target_user_id: int, subscriber_user_id: int) -> None:
        if target_user_id in self.auto_translate_targets:
            self.auto_translate_targets[target_user_id].discard(subscriber_user_id)
            if not self.auto_translate_targets[target_user_id]:
                self.auto_translate_targets.pop(target_user_id)
        if not self.dbms:
            return
        self.dbms.delete_data("auto_translate", {"target_user_id": target_user_id, "subscriber_user_id": subscriber_user_id})

    def register_command(self, command: str, callback: callable, description: str = "", option_name: str | None = None, choices: list[str] | None = None, context_menu: bool = False, user_option: bool = False) -> bool:
        if command in self.commands or (context_menu and f'context_{command}' in self.commands):
            return False

        if context_menu:
            @self.tree.context_menu(name=command)
            async def context_command(interaction: discord.Interaction, message: discord.Message):
                await callback(interaction, message)
                self._update_command_usage(command)

            self.commands[f'context_{command}'] = callback
            self._save_command(command, description or f'{command} context menu')
            return True

        if user_option:
            @self.tree.command(name=command, description=description or f'{command} command')
            @app_commands.describe(target="Select a user")
            async def slash_command(interaction: discord.Interaction, target: discord.Member):
                await callback(interaction, target)
                self._update_command_usage(command)
        elif option_name and choices:
            trimmed_choices = [c for c in choices if c][:25]

            @self.tree.command(name=command, description=description or f'{command} command')
            @app_commands.rename(selection=option_name)
            @app_commands.describe(selection=f'Select {option_name}')
            @app_commands.choices(selection=[app_commands.Choice(name=choice, value=choice) for choice in trimmed_choices])
            async def slash_command(interaction: discord.Interaction, selection: app_commands.Choice[str]):
                await callback(interaction, selection.value)
                self._update_command_usage(command)
        else:

            @self.tree.command(name=command, description=description or f'{command} command')
            async def slash_command(interaction: discord.Interaction):
                await callback(interaction)
                self._update_command_usage(command)

        self.commands[command] = callback
        self._save_command(command, description or f'{command} command')
        return True
            
    def _update_connected_guilds(self) -> None:
        """Update the connected guilds statistic in the database, if available."""
        if not self.dbms:
            return
        try:
            guild_count = len(self.client.guilds)
            self.guild_count = guild_count

            # Persist live guild count so admin panels reflect current state.
            self.dbms.update_data("statistics", {}, {"connected_guilds": guild_count})
            self.logging(f'Connected guilds updated: {guild_count}')

        except Exception as error:
            self.logging(f'Error updating connected guilds: {error}')

    def _save_message(self, message_data: dict) -> None:
        """Persist a public guild message to the database and update statistics.

        Args:
            message_data (dict): Serialized message payload.
        """
        if not self.dbms:
            return
        try:
            self.dbms.insert_data("messages", message_data)
            self._increment_message_stats()
        except Exception as error:
            self.logging(f'Error saving message: {error}')
    
    def _save_direct_message(self, dm_data: dict) -> None:
        """Persist a direct message to the database and update statistics.

        Args:
            dm_data (dict): Serialized DM payload.
        """
        if not self.dbms:
            return
        try:
            self.dbms.insert_data("direct_messages", dm_data)
            self._increment_dm_stats()
        except Exception as error:
            self.logging(f'Error saving direct message: {error}')
    
    def _save_command(self, command_name: str, description: str) -> None:
        """Ensure a command row exists in the `commands` table.

        Args:
            command_name (str): Name of the command.
            description (str): Human-readable description.
        """
        if not self.dbms:
            return
        try:
            existing = self.dbms.get_data("commands", {"command_name": command_name})
            if not existing:
                command_data = {
                    "command_name": command_name,
                    "description": description,
                    "usage_count": 0,
                    "last_used": None,
                    "enabled": True
                }
                self.dbms.insert_data("commands", command_data)
        except Exception as error:
            self.logging(f'Error saving command: {error}')
    
    def _update_command_usage(self, command_name: str) -> None:
        """Increment usage counters for a command and update statistics.

        Args:
            command_name (str): Name of the command that was invoked.
        """
        if not self.dbms:
            return
        try:
            commands = self.dbms.get_data("commands", {"command_name": command_name})
            if commands:
                command = commands[0]
                command["usage_count"] = command.get("usage_count", 0) + 1
                command["last_used"] = datetime.now().isoformat()
                self.dbms.update_data("commands", {"command_name": command_name}, command)
                self._increment_command_stats(command_name)
        except Exception as error:
            self.logging(f'Error updating command usage: {error}')
    
    def _increment_message_stats(self) -> None:
        """Increment the daily total message counter in statistics."""
        if not self.dbms:
            return
        try:
            today = datetime.now().date().isoformat()
            stats = self.dbms.get_data("statistics", {"date": today})
            if stats:
                stat = stats[0]
                stat["total_messages"] = stat.get("total_messages", 0) + 1
                self.dbms.update_data("statistics", {"date": today}, stat)
        except Exception as error:
            self.logging(f'Error updating message stats: {error}')
    
    def _increment_dm_stats(self) -> None:
        """Increment the daily total DM counter in statistics."""
        if not self.dbms:
            return
        try:
            today = datetime.now().date().isoformat()
            stats = self.dbms.get_data("statistics", {"date": today})
            if stats:
                stat = stats[0]
                stat["total_dms"] = stat.get("total_dms", 0) + 1
                self.dbms.update_data("statistics", {"date": today}, stat)
        except Exception as error:
            self.logging(f'Error updating DM stats: {error}')
    
    def _increment_command_stats(self, command_name: str) -> None:
        """Increment the daily command counters for the given command.

        Args:
            command_name (str): Command whose usage should be counted.
        """
        if not self.dbms:
            return
        try:
            today = datetime.now().date().isoformat()
            stats = self.dbms.get_data("statistics", {"date": today})
            if stats:
                stat = stats[0]
                stat["total_commands"] = stat.get("total_commands", 0) + 1
                if "command_breakdown" not in stat:
                    stat["command_breakdown"] = {}
                stat["command_breakdown"][command_name] = stat["command_breakdown"].get(command_name, 0) + 1
                self.dbms.update_data("statistics", {"date": today}, stat)
        except Exception as error:
            self.logging(f'Error updating command stats: {error}')

    def _load_auto_translate_targets(self) -> None:
        """Load all auto-translate target subscriptions from the database."""
        try:
            targets: dict[int, set[int]] = {}
            for record in self.dbms.get_data("auto_translate", {}):
                try:
                    target = int(record.get("target_user_id"))
                    subscriber = int(record.get("subscriber_user_id"))
                except (TypeError, ValueError):
                    continue
                targets.setdefault(target, set()).add(subscriber)
            self.auto_translate_targets = targets
        except Exception as error:
            self.logging(f'Error loading auto-translate targets: {error}')

if __name__ == "__main__":
    from discord_bot.adapters.db import DBMS
    from discord_bot.init.config_loader import DBConfigLoader
    
    dbms = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    dbms.connect()
    
    bot = DiscordLogic(dbms=dbms)
    
    async def funfact_command(interaction: discord.Interaction):
        await interaction.response.send_message("Hallo Welt!")
    
    bot.register_command("test", funfact_command, description="Test command")
    bot.run()
