import discord
from discord_bot.init.config_loader import DiscordConfig

class DiscordBot:
    def __init__(self):
        self.client = discord.Client(intents=discord.Intents.default())
        self.client.event(self.on_ready)
    
    async def on_ready(self):
        print(f'Logged in as {self.client.user}')
    
    def run(self):
        self.client.run(DiscordConfig.DISCORD_TOKEN)

if __name__ == '__main__':
    bot = DiscordBot()
    bot.run()
