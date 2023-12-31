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

    # VCに接続するコマンド
    if message.content.startswith(f"{COMMAND_PREFIX}join"):
        # メッセージを送信したユーザーがVCにいるか確認
        if message.author.voice:
            channel = message.author.voice.channel
            await channel.connect()  # VCに接続
            await message.channel.send(f"{channel.name}に接続しました。")
        else:
            await message.channel.send("あなたはボイスチャンネルにいません。")


bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
