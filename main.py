from functools import partial
import logging
import discord
from discord.ext import commands
import os
from commands import join, leave
from utils import handle_message, handle_voice_state_update, load_style_settings
from bot_commands import setup_commands
from settings import APPROVED_GUILD_IDS, BOT_PREFIX, GAME_NAME
from voice import VoiceSynthServer


def setup_commands(server, bot, speaker_settings):
    # joinコマンド用の部分関数を作成
    join_partial = partial(join, server=server, speaker_settings=speaker_settings)

    # joinコマンドを登録
    join_command = bot.tree.command(
        name="join",
        guilds=APPROVED_GUILD_IDS,
        description="ボットをボイスチャンネルに接続し、読み上げを開始します。",
    )(join_partial)
    bot.tree.add_command(join_command)

    # leaveコマンド用の部分関数を作成
    leave_partial = partial(leave, server=server, speaker_settings=speaker_settings)

    # leaveコマンドを登録
    leave_command = bot.tree.command(
        name="leave", guilds=APPROVED_GUILD_IDS, description="ボットをボイスチャンネルから切断します。"
    )(leave_partial)
    bot.tree.add_command(leave_command)


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)
    server = VoiceSynthServer()
    speaker_settings = load_style_settings()
    setup_commands(server, bot, speaker_settings)

    @bot.event
    async def on_ready():
        try:
            logging.info(f"Logged in as {bot.user.name}")
            await bot.change_presence(activity=discord.Game(name=GAME_NAME))
            for guild in APPROVED_GUILD_IDS:
                await bot.tree.sync(guild=guild)
            for guild in bot.guilds:
                bot.loop.create_task(server.process_playback_queue(str(guild.id)))
        except Exception as e:
            logging.error(f"Error occurred: {e}")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        await bot.process_commands(message)
        await handle_message(server, bot, message)

    @bot.event
    async def on_voice_state_update(member, before, after):
        await handle_voice_state_update(server, bot, member, before, after)

    bot.run(os.getenv("VOICECHATLOIDTEST_TOKEN"))
