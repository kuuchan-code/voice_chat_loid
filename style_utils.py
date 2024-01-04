# style_utils.py
import json
from settings import (
    STYLE_SETTINGS_FILE,
    speaker_settings,
    USER_DEFAULT_STYLE_ID,
    ANNOUNCEMENT_DEFAULT_STYLE_ID,
)


def update_style_setting(guild_id, user_id, style_id, voice_scope):
    if voice_scope == "user_default":
        speaker_settings[guild_id]["user_default"] = style_id
    elif voice_scope == "announcement":
        speaker_settings[guild_id]["announcement"] = style_id
    elif voice_scope == "user":
        speaker_settings[user_id] = style_id
    save_style_settings()


def get_current_style_details(guild_id, user_id, voice_scope):
    if voice_scope == "user_default":
        style_id = speaker_settings[guild_id].get("user_default", USER_DEFAULT_STYLE_ID)
    elif voice_scope == "announcement":
        style_id = speaker_settings[guild_id].get(
            "announcement", ANNOUNCEMENT_DEFAULT_STYLE_ID
        )
    elif voice_scope == "user":
        style_id = speaker_settings.get(user_id, USER_DEFAULT_STYLE_ID)

    speaker_name, style_name = get_style_details(style_id)
    return style_id, speaker_name, style_name


def save_style_settings():
    """スタイル設定を保存します。"""
    with open(STYLE_SETTINGS_FILE, "w") as f:
        json.dump(speaker_settings, f)


def load_style_settings():
    """スタイル設定をロードします。"""
    try:
        with open(STYLE_SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}