import os
import json
import discord
from typing import List, Dict


class ConfigError(Exception):
    pass


class BotSettings:
    def __init__(self, config: Dict):
        self.BOT_PREFIX = config.get("bot_prefix", "!")
        self.GAME_NAME = config.get("game_name", "リクエストを待機中")
        self.MAX_MESSAGE_LENGTH = config.get("max_message_length", 200)
        self.validate()

    def validate(self):
        if not isinstance(self.MAX_MESSAGE_LENGTH, int):
            raise ConfigError("max_message_length must be an integer")


class VoiceVoxSettings:
    def __init__(self, config: Dict):
        self.ENGINE_URL = config["engine_url"]
        self.SPEAKERS_URL = config["speakers_url"]
        self.AUDIO_QUERY_URL = config["audio_query_url"]
        self.SYNTHESIS_URL = config["synthesis_url"]
        # self.validate()

    def validate(self):
        required_keys = [
            "engine_url",
            "speakers_url",
            "audio_query_url",
            "synthesis_url",
        ]
        for key in required_keys:
            if key not in self.__dict__:
                raise ConfigError(f"{key} is required in VoiceVoxSettings")


def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config


config = load_config()

bot_settings = BotSettings(config.get("bot_settings", {}))
voicevox_settings = VoiceVoxSettings(config["voicevox_settings"])
approved_guild_ids_int = config["guild_settings"]["approved_guild_ids"]
approved_guild_objects = [
    discord.Object(id=guild_id) for guild_id in approved_guild_ids_int
]
error_messages = config["error_messages"]
info_messages = config["info_messages"]

TOKEN = os.getenv("VOICECHATLOIDTEST_TOKEN")
USER_DEFAULT_STYLE_ID = 3
ANNOUNCEMENT_DEFAULT_STYLE_ID = 8
script_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_PICKLE_FILE = os.path.join(script_dir, "config.pkl")

# CHARACTERS_INFO.json に移動
with open("characters_info.json", "r") as f:
    CHARACTORS_INFO = json.load(f)

DORMITORY_URL_BASE = "https://voicevox.hiroshiba.jp/dormitory"
