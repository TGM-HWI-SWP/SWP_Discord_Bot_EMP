import discord
from discord_bot.init.config_loader import DiscordConfig

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!hello'):
        await message.channel.send(f'Hello {message.author.mention}!')

def run():
    client.run(DiscordConfig.DISCORD_TOKEN)

if __name__ == '__main__':
    run()
