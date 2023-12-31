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
        character_id = CHARACTORS_INFO.get(name, "unknown")  # キャラクターIDを取得
        url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
        styles = ", ".join(
            [f"{style['name']} (ID: {style['id']})" for style in speaker["styles"]]
        )
        message += f"\n[{name}]({url}): {styles}"

    # 長いメッセージを適切に分割して送信
    await send_long_message(ctx, message)

async def send_long_message(ctx, message, split_char='\n'):
    """2000文字を超える長いメッセージを適切に分割して送信します。"""
    while len(message) > 0:
        # メッセージが2000文字以下の場合はそのまま送信
        if len(message) <= 2000:
            await ctx.send(message)
            break
        # メッセージを2000文字で仮に切り分け
        part = message[:2000]
        # 最後の改行位置または分割文字の位置を探す
        split_pos = part.rfind(split_char)
        if split_pos == -1:
            # 分割文字が見つからない場合は、2000文字で強制的に分割
            split_pos = 1999
        # 最初の部分を送信
        await ctx.send(message[:split_pos + 1])
        # 残りのメッセージを更新
        message = message[split_pos + 1:]
@bot.command(name="join")
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"{channel.name}に接続しました。")
    else:
        await ctx.send("あなたはボイスチャンネルにいません。")


bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
