import discord
from discord_bot.init.config_loader import DiscordConfig

client = discord.Client(intents=discord.Intents.default())

TARGET_USER_ID = 577154967740219403  # Hier die User ID eingeben

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    
    user = await client.fetch_user(TARGET_USER_ID)
    await user.send("Oida, griass di! I bin der LeberkasLarry, dein persönlicher Jausen-Buddy aus’m schönen Österreich! 😎 Ob du Hunger auf a bissl Schmäh, a witzigen Fun-Fact oder a richtig g’scheite Portion Leberkas brauchst – i steh bereit. 🥖🧡 Schmeiß di auf die Couch, klick a bissl rum und lass uns gemeinsam de Zeit versüßen – versprochen, es werd lustig und liab! Ach ja, koa Angst – i bin halb Maschine, halb Fleischlaib, 100% leiwand. 😏 Pfiat di bis gleich! Dein Larry 🍀")

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
