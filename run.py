import os
import discord
import logging
from discord.ext import commands
from bot_commands import setup_commands
from settings import (
    COMMAND_PREFIX,
    TEST_GUILD_ID,
)

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix=COMMAND_PREFIX)


@bot.event
async def on_ready():
    logging.info(f"ログインしました。ユーザー名: {bot.user.name}!")
    await bot.tree.sync(guild=TEST_GUILD_ID)
    setup_commands(bot)

bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
