import os
import discord

from settings import (
    CHARACTORS_INFO,
    COMMAND_PREFIX,
    SPEAKERS_URL,
    USER_DEFAULT_STYLE_ID,
)
from discord.ext import commands

from voicevox_client import audio_query, fetch_json, synthesis

import asyncio
from discord import FFmpegPCMAudio
from discord.utils import get

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix=COMMAND_PREFIX)

speakers_data = fetch_json(SPEAKERS_URL)
print(speakers_data)


class ServerSettings:
    def __init__(self):
        self.voice_client = None
        self.queue = asyncio.Queue()
        self.current_settings = {}

    def update_setting(self, setting_key, value):
        self.current_settings[setting_key] = value

    async def play_next_in_queue(self):
        while True:
            if self.voice_client.is_playing():
                await asyncio.sleep(1)
            else:
                query_data = await self.queue.get()
                print(query_data)
                if query_data:
                    audio = await synthesis(query_data['style_id'], query_data['query_data'])
                    if audio:
                        self.voice_client.play(FFmpegPCMAudio(io.BytesIO(audio), pipe=True))
                self.queue.task_done()


server_settings = {}


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


async def send_long_message(ctx, message, split_char="\n"):
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
        await ctx.send(message[: split_pos + 1])
        # 残りのメッセージを更新
        message = message[split_pos + 1 :]


@bot.command(name="join")
async def join(ctx):
    global server_settings
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = get(bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()
        if ctx.guild.id not in server_settings:
            server_settings[ctx.guild.id] = ServerSettings()
        server_settings[ctx.guild.id].voice_client = voice_client
        await ctx.send(f"{channel.name}に接続しました。")
    else:
        await ctx.send("あなたはボイスチャンネルにいません。")


@bot.command(name="leave")
async def leave(ctx):
    voice_client = get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("チャンネルから切断しました。")
    else:
        await ctx.send("ボットはどのチャンネルにも接続していません。")


@bot.event
async def on_message(message):
    if message.author == bot.user or not message.guild:
        return

    text = message.content  # メッセージ内容を取得
    settings = server_settings.get(message.guild.id)
    if settings and settings.voice_client:
        # ユーザーがスタイルIDを設定していない場合、デフォルトのIDを使用
        style_id = settings.current_settings.get("style_id", USER_DEFAULT_STYLE_ID)
        
        # audio_query関数にtextとstyle_idを渡す
        query_data = await audio_query(text, style_id)
        if query_data:
            await settings.queue.put(
                {
                    "style_id": style_id,
                    "query_data": query_data,
                }
            )
            if not settings.voice_client.is_playing():
                await settings.play_next_in_queue()

    await bot.process_commands(message)



@bot.command(name="skip")
async def skip(ctx):
    settings = server_settings.get(ctx.guild.id)
    if settings and settings.voice_client.is_playing():
        settings.voice_client.stop()
        await ctx.send("現在の読み上げをスキップしました。")


@bot.command(name="clear")
async def clear(ctx):
    settings = server_settings.get(ctx.guild.id)
    if settings:
        settings.queue = asyncio.Queue()
        await ctx.send("キューをクリアしました。")


bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
