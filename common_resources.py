
import json
from settings import STYLE_SETTINGS_FILE


def load_style_settings():
    """スタイル設定をロードします。"""
    try:
        with open(STYLE_SETTINGS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}