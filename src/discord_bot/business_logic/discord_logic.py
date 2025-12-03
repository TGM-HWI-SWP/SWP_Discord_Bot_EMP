import discord
import asyncio

from discord_bot.init.config_loader import DiscordConfig
from discord_bot.contracts.ports import DiscordBotPort

class DiscordBot(DiscordBotPort):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        self.commands = {}
        self.command_prefix = DiscordConfig.COMMAND_PREFIX
        
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

    async def on_message(self, message):
        if message.author == self.client.user:
            return
        
        if message.content.startswith(self.command_prefix):
            parts = message.content[1:].split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if command in self.commands:
                await self.commands[command](message, args)

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
        self.commands[command] = callback
        return True

if __name__ == '__main__':
    bot = DiscordBot()
    
    async def funfact_command(message, args):
        await message.channel.send("Here's a fun fact!")
    
    bot.register_command("funfact", funfact_command)
    bot.run()
