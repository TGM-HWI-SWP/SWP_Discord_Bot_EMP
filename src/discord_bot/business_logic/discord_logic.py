import asyncio
from datetime import datetime
import discord
from discord import app_commands

from discord_bot.contracts.ports import DiscordLogicPort, DatabasePort
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
        self.commands = {}
        self.unread_dms = []
        self.dbms = dbms
        
        @self.client.event
        async def on_ready():
            await self.on_ready()
        
        @self.client.event
        async def on_message(message):
            await self.on_message(message)
    
    def execute_function(self):
        pass
    
    def run(self):
        self.logging("Starting Discord bot...")
        self.client.run(DiscordConfigLoader.DISCORD_TOKEN)
    
    def stop(self):
        asyncio.create_task(self.client.close())

    async def on_ready(self):
        self.logging(f'Logged in as {self.client.user}')
        
        await self.tree.sync()
        self.logging(f'Synced {len(self.tree.get_commands())} slash commands globally')
        
        for guild in self.client.guilds:
            await self.tree.sync(guild=guild)
            self.logging(f'Synced to guild: {guild.name}')

    async def on_message(self, message):
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
                "is_command": message.content.startswith("/")
            }
            self.unread_dms.append(dm_data)
            self._save_direct_message(dm_data)
        else:
            message_data = {
                "message_id": message.id,
                "server_id": message.guild.id if message.guild else None,
                "channel_id": message.channel.id,
                "user_id": message.author.id,
                "user_name": str(message.author),
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "is_command": message.content.startswith("/")
            }
            self._save_message(message_data)
    
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

    def send_message(self, server_id: int, channel_id: int, message: str) -> bool:
        try:
            channel = self.client.get_channel(channel_id)
            if not channel:
                return False
            
            # If server_id is 0, skip server check (DM or any channel)
            if server_id != 0 and hasattr(channel, 'guild') and channel.guild.id != server_id:
                return False
            
            async def _send():
                await channel.send(message)
            
            asyncio.create_task(_send())
            return True
        except Exception:
            return False

    def send_dm(self, user_id: int, message: str) -> bool:
        try:
            user = self.client.get_user(user_id)
            if not user:
                return False
            
            async def _send():
                await user.send(message)
            
            asyncio.create_task(_send())
            return True
        except Exception:
            return False

    def get_servers(self) -> list[dict]:
        return [{"id": guild.id, "name": guild.name} for guild in self.client.guilds]
    
    def get_guild_info(self, server_id: int) -> dict | None:
        
        guild = self.client.get_guild(server_id)
        if guild:
            return {
                "id": guild.id,
                "name": guild.name,
                "member_count": guild.member_count
            }
        return None

    def leave_server(self, server_id: int) -> bool:
        try:
            guild = self.client.get_guild(server_id)
            if not guild:
                return False
            
            async def _leave():
                await guild.leave()
            
            asyncio.create_task(_leave())
            return True
        except Exception:
            return False

    def block_user(self, user_id: int) -> bool:
        try:
            user = self.client.get_user(user_id)
            if not user:
                return False
            
            async def _block():
                await user.block()
            
            asyncio.create_task(_block())
            return True
        except Exception:
            return False
    
    def unblock_user(self, user_id: int) -> bool:
        try:
            user = self.client.get_user(user_id)
            if not user:
                return False
            
            async def _unblock():
                await user.unblock()
            
            asyncio.create_task(_unblock())
            return True
        except Exception:
            return False

    def get_channels(self, server_id: int) -> list[dict]:
        guild = self.client.get_guild(server_id)
        if not guild:
            return []
        return [{"id": channel.id, "name": channel.name} for channel in guild.text_channels]

    def is_connected(self) -> bool:
        return self.client.is_ready()
    
    def get_bot_stats(self) -> dict:
        """Get bot statistics: status, server count, and total user count"""
        if not self.is_connected():
            return {"status": "Offline", "servers": 0, "users": 0}
        
        try:
            total_members = sum(guild.member_count for guild in self.client.guilds)
            return {
                "status": "Online",
                "servers": len(self.client.guilds),
                "users": total_members
            }
        except Exception as e:
            self.logging(f"Error getting bot stats: {e}")
            return {"status": "Error", "servers": 0, "users": 0}

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

    def register_command(self, command: str, callback: callable, description: str = "") -> bool:
        if command in self.commands:
            return False
        
        @self.tree.command(name=command, description=description or f"{command} command")
        async def slash_command(interaction: discord.Interaction):
            await callback(interaction)
            self._update_command_usage(command)
        
        self.commands[command] = callback
        self._save_command(command, description or f"{command} command")
        return True
    
    def _save_message(self, message_data: dict) -> None:
        if not self.dbms:
            return
        try:
            self.dbms.insert_data("messages", message_data)
            self._increment_message_stats()
        except Exception as error:
            self.logging(f'Error saving message: {error}')
    
    def _save_direct_message(self, dm_data: dict) -> None:
        if not self.dbms:
            return
        try:
            self.dbms.insert_data("direct_messages", dm_data)
            self._increment_dm_stats()
        except Exception as error:
            self.logging(f'Error saving direct message: {error}')
    
    def _save_command(self, command_name: str, description: str) -> None:
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

if __name__ == '__main__':
    from discord_bot.adapters.db import DBMS
    from discord_bot.init.config_loader import DBConfigLoader
    
    dbms = DBMS(db_name=DBConfigLoader.DISCORD_DB_NAME)
    dbms.connect()
    
    bot = DiscordLogic(dbms=dbms)
    
    async def funfact_command(interaction: discord.Interaction):
        await interaction.response.send_message("Hallo Welt!")
    
    bot.register_command("test", funfact_command, description="Test command")
    bot.run()
