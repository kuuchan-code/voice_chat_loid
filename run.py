import os
import discord
from bot_commands import setup_commands

from settings import COMMAND_PREFIX
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix=COMMAND_PREFIX)
setup_commands(bot)


@bot.event
async def on_ready():
    print(f"ログインしました。ユーザー名: {bot.user.name}!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
