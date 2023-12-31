import os
import discord

from settings import CHARACTORS_INFO, COMMAND_PREFIX, SPEAKERS_ENDPOINT
from discord.ext import commands

from voicevox_client import fetch_json


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix=COMMAND_PREFIX)

speakers_data = fetch_json(SPEAKERS_ENDPOINT)
print(speakers_data)

@bot.event
async def on_ready():
    print(f"ログインしました。ユーザー名: {bot.user.name}!")


@bot.command(name="list", help="スピーカーとそのスタイルIDを表示します。")
async def list(ctx):
    """スピーカーとそのスタイルIDを表示します。"""
    if not speakers_data:
        await ctx.send("スピーカーのデータを取得できませんでした。")
        return

    # メッセージを整形して作成
    message = "**利用可能なスピーカーとスタイル:**\n"
    for speaker in speakers_data:
        name = speaker["name"]
        if name == "ナースロボ＿タイプＴ":
            continue
        elif name == "†聖騎士 紅桜†":
            continue
        else:
            character_id = CHARACTORS_INFO.get(name, "unknown")  # キャラクターIDを取得
            url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
            styles = ", ".join(
                [f"{style['name']} (ID: {style['id']})" for style in speaker["styles"]]
            )
            message += f"\n[{name}]({url}): {styles}"

    # メッセージの長さが2000文字を超えないように調整
    if len(message) > 2000:
        await ctx.send(message[:2000])
        await ctx.send(message[2000:])
    else:
        await ctx.send(message)


@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"{channel.name}に接続しました。")
    else:
        await ctx.send("あなたはボイスチャンネルにいません。")


bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
