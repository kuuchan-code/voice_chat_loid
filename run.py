import os
import discord
from bot_commands import setup_commands

from settings import COMMAND_PREFIX
from voicevox_client import fetch_json

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents, command_prefix=COMMAND_PREFIX)
setup_commands(client)

@client.event
async def on_ready():
    print(f"ログインしました。ユーザー名: {client.user.name}!")


@client.event
async def on_message(message):
    if message.author == client.user:
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


client.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
