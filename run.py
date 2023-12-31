import os
import discord
import logging
from discord.ext import commands
from settings import COMMAND_PREFIX, SPEAKERS_ENDPOINT
from voicevox_client import fetch_json

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    speakers_data = await fetch_json(SPEAKERS_ENDPOINT)

    if speakers_data:
        logging.info(speakers_data)
    else:
        logging.error("データの取得に失敗しました。")

    logging.info(f"ログインしました。ユーザー名: {bot.user.name}!")


@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"{channel.name}に接続しました。")
    else:
        await ctx.send("あなたはボイスチャンネルにいません。")


@bot.command(name="list_styles", aliases=["ls"])
async def list_styles(ctx):
    """スピーカーとそのスタイルを表示します。"""
    speakers_data = await fetch_json(SPEAKERS_ENDPOINT)  # 非同期でJSONデータを取得

    if not speakers_data:
        await ctx.send("スピーカーのデータを取得できませんでした。")
        return

    # メッセージを整形して作成
    message = "**利用可能なスピーカーとスタイル:**\n"
    for speaker in speakers_data:
        name = speaker["name"]
        styles = ", ".join([style["name"] for style in speaker["styles"]])
        message += f"\n**{name}**: {styles}"

    # メッセージの長さが2000文字を超えないように調整
    if len(message) > 2000:
        await ctx.send(message[:2000])
        await ctx.send(message[2000:])
    else:
        await ctx.send(message)


bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
