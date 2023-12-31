import discord

intents = discord.Intents.default()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'ログインしました。ユーザー名: {client.user.name}!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('こんにちは!')

client.run('YOUR_TOKEN')
