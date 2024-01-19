#!/usr/bin/python3
import asyncio
import logging
import os
import aiohttp
import discord
from discord.ext import commands
from SpeechTextFormatter import SpeechTextFormatter
from VoiceSynthEventProcessor import VoiceSynthEventProcessor
from commands.add_channel import setup_additional_channel_command
from commands.settings import setup_settings_command
from commands.info import setup_info_command
from commands.join import setup_join_command
from commands.leave import setup_leave_command
from commands.skip import setup_skip_command
from commands.help import setup_help_command
from VoiceSynthConfig import VoiceSynthConfig
from settings_loader import (
    BotSettings,
    GlobalSettings,
    VOICEVOXSettings,
)
from VoiceSynthService import VoiceSynthService
import logging.handlers

# Define a safe log file path, e.g., in the home directory
home_dir = os.path.expanduser("~")
log_file_path = os.path.join(home_dir, "discord.log")
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
logging.getLogger("discord.http").setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename=log_file_path,
    encoding="utf-8",
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
formatter.default_msec_format = "%s.%04d"


async def is_synth_service_up(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                return response.status == 200
        except Exception as e:
            logging.error(f"Error checking service status: {e}")
            return False


async def wait_for_synth_service(url, max_attempts=10, delay=5):
    attempts = 0
    while attempts < max_attempts:
        if await is_synth_service_up(url):
            logging.info("Server is up!")
            return True
        await asyncio.sleep(delay)
        attempts += 1
    return False


async def main():
    try:
        # 非同期処理に変更
        if await wait_for_synth_service(
            VOICEVOXSettings.LOCAL_ENGINE_URL + VOICEVOXSettings.SPEAKERS_URL
        ):
            intents = discord.Intents.default()
            intents.message_content = True
            bot = commands.Bot(command_prefix=BotSettings.BOT_PREFIX, intents=intents)
            synth_service = VoiceSynthService()
            asyncio.create_task(synth_service.check_and_update_active_engines(1))
            await synth_service.ensure_session()
            synth_config = VoiceSynthConfig()
            await synth_config.async_init()
            text_processor = SpeechTextFormatter()
            synth_event_processor = VoiceSynthEventProcessor(
                synth_config, synth_service, text_processor
            )

            setup_join_command(bot, synth_service, synth_config, text_processor)
            setup_leave_command(bot, synth_service, synth_config)
            setup_settings_command(bot, synth_config)
            setup_info_command(bot, synth_config)
            setup_skip_command(bot, synth_service)
            setup_help_command(bot)
            setup_additional_channel_command(bot, synth_config)

            @bot.event
            async def on_ready():
                try:
                    logging.info(f"Logged in as {bot.user.name}")
                    await bot.change_presence(
                        activity=discord.Game(name=BotSettings.GAME_NAME)
                    )
                    await bot.tree.sync()
                    for guild in bot.guilds:
                        logging.info(f"Guild ID: {guild.id}, Name: {guild.name}")
                        try:
                            if guild:
                                bot.loop.create_task(
                                    synth_service.process_playback_queue(guild.id)
                                )
                            else:
                                logging.error(
                                    f"Unable to find guild with ID: {guild.name}"
                                )
                        except Exception as e:
                            logging.error(
                                f"Error syncing commands for guild {guild.name}: {e}"
                            )
                except Exception as e:
                    logging.error(f"Error occurred in on_ready: {e}")

            @bot.event
            async def on_guild_join(guild):
                logging.info(f"Joined new guild: {guild.name}")
                bot.loop.create_task(synth_service.process_playback_queue(guild.id))

            @bot.event
            async def on_message(message: discord.Message):
                if message.author.bot:  # これでメッセージがボットからのものかどうかをチェック
                    return
                await bot.process_commands(message)
                await synth_event_processor.handle_message(message)

            @bot.event
            async def on_voice_state_update(member: discord.Member, before, after):
                await synth_event_processor.handle_voice_state_update(
                    bot,
                    member,
                    before,
                    after,
                )

            # bot.run()の代わりにbot.start()を使用します
            await bot.start(GlobalSettings.TOKEN)
            await synth_service.close()
        else:
            logging.error("Server did not become available in time. Exiting.")
    except Exception as e:
        logging.error(f"Unexpected error in main function: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
