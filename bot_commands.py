import logging
import discord
from settings import (
    ANNOUNCEMENT_URL_BASE,
    APPROVED_GUILD_IDS,
    ERROR_MESSAGES,
    USER_DEFAULT_STYLE_ID,
    ANNOUNCEMENT_DEFAULT_STYLE_ID,
)
from utils import (
    get_character_info,
    speaker_settings,
    save_style_settings,
    get_style_details,
)
from commands import leave, join

# voice_scope_description = {
#     "user": f"{user_display_name}さんのテキスト読み上げ音声",
#     "announcement": "アナウンス音声",
#     "user_default": "ユーザーデフォルトTTS音声",
# }


# # もち子さんの場合、特別なクレジット表記を使用
# if speaker_name == "もち子さん":
#     speaker_name = "もち子(cv 明日葉よもぎ)"
# コマンド設定関数
def setup_commands(bot):
    # ボットをボイスチャンネルに接続し、読み上げを開始するコマンド
    join_command = bot.tree.command(
        name="join", guilds=APPROVED_GUILD_IDS, description="ボットをボイスチャンネルに接続し、読み上げを開始します。"
    )(join)
    bot.tree.add_command(join_command)


    # ボットをボイスチャンネルから切断するコマンド
    leave_command = bot.tree.command(
        name="leave", guilds=APPROVED_GUILD_IDS, description="ボットをボイスチャンネルから切断します。"
    )(leave)
    bot.tree.add_command(leave_command)