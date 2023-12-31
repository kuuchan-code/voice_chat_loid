import os
import discord
import logging
from discord.ext import commands
from settings import (
    CHARACTORS_INFO,
    COMMAND_PREFIX,
    SPEAKERS_ENDPOINT,
)
from voicevox_client import fetch_json

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    logging.info(f"ログインしました。ユーザー名: {bot.user.name}!")


bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
