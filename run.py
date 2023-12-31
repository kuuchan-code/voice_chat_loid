import os
import discord

# Create an instance of a Client, this is your connection to Discord
client = discord.Client()

# Event listener for when the bot has switched from offline to online
@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')

# Event listener for when a message is sent to a channel the bot has access to
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

# Run the bot with the token
client.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
