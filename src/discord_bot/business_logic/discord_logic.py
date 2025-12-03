import discord
from discord import app_commands
import asyncio

from discord_bot.init.config_loader import DiscordConfig
from discord_bot.contracts.ports import DiscordBotPort

class DiscordBot(DiscordBotPort):
    def __init__(self):
        intents = discord.Intents.default()
        self.client = discord.Client(intents=intents)
        self.tree = app_commands.CommandTree(self.client)
        self.commands = {}
        self.unread_dms = []
        
        @self.client.event
        async def on_ready():
            await self.on_ready()
        
        @self.client.event
        async def on_message(message):
            await self.on_message(message)
    
    def run(self):
        self.client.run(DiscordConfig.DISCORD_TOKEN)
    
    def stop(self):
        asyncio.create_task(self.client.close())

    async def on_ready(self):
        print(f'Logged in as {self.client.user}')
        
        await self.tree.sync()
        print(f'Synced {len(self.tree.get_commands())} slash commands globally')
        
        for guild in self.client.guilds:
            await self.tree.sync(guild=guild)
            print(f'Synced to guild: {guild.name}')

    async def on_message(self, message):
        if message.author == self.client.user:
            return
        
        if isinstance(message.channel, discord.DMChannel):
            dm_data = {
                "id": message.id,
                "author_id": message.author.id,
                "author_name": str(message.author),
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "read": False
            }
            self.unread_dms.append(dm_data)
    
    def get_unread_dms(self) -> list[dict]:
        return [dm for dm in self.unread_dms if not dm["read"]]
    
    def mark_dm_as_read(self, dm_id: int) -> bool:
        for dm in self.unread_dms:
            if dm["id"] == dm_id and not dm["read"]:
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
            if channel and channel.guild.id == server_id:
                asyncio.create_task(channel.send(message))
                return True
            return False
        except:
            return False

    def send_dm(self, user_id: int, message: str) -> bool:
        try:
            user = self.client.get_user(user_id)
            if user:
                asyncio.create_task(user.send(message))
                return True
            return False
        except:
            return False

    def get_servers(self) -> list[dict]:
        return [{"id": guild.id, "name": guild.name} for guild in self.client.guilds]

    def get_channels(self, server_id: int) -> list[dict]:
        guild = self.client.get_guild(server_id)
        if not guild:
            return []
        return [{"id": channel.id, "name": channel.name} for channel in guild.text_channels]

    def is_connected(self) -> bool:
        return self.client.is_ready()

    def register_command(self, command: str, callback) -> bool:
        if command in self.commands:
            return False
        
        @self.tree.command(name=command, description=f"{command} command")
        async def slash_command(interaction: discord.Interaction):
            await callback(interaction)
        
        self.commands[command] = callback
        return True

if __name__ == '__main__':
    bot = DiscordBot()
    
    async def funfact_command(interaction: discord.Interaction):
        await interaction.response.send_message("Hallo Welt!")
    
    bot.register_command("test", funfact_command)
    bot.run()
