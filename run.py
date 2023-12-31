import os
import discord

from settings import COMMAND_PREFIX, SPEAKERS_URL
from voicevox_client import fetch_json

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents, command_prefix=COMMAND_PREFIX)


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


speakers_data = fetch_json(SPEAKERS_URL)

if speakers_data:
    print(speakers_data)  # JSONデータを表示
else:
    print("データの取得に失敗しました。")


client.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
