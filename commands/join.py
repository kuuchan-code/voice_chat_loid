import logging
import discord

from settings import ANNOUNCEMENT_DEFAULT_STYLE_ID, ANNOUNCEMENT_URL_BASE, ERROR_MESSAGES, USER_DEFAULT_STYLE_ID
from utils import get_character_info, get_style_details, save_style_settings


async def join(interaction: discord.Interaction, server, speaker_settings):
    await interaction.response.defer()
    voice_client = await handle_join_request(interaction)
    if voice_client:
        await welcome_user(server, interaction, voice_client, speaker_settings)
        try_save_style_settings()



# 接続と歓迎の機能を分割し、それぞれの責務を明確にします。
async def handle_join_request(interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.followup.send(ERROR_MESSAGES["connection"])
        return None

    try:
        voice_client = await connect_to_voice_channel(interaction)
        return voice_client
    except discord.ClientException as e:
        logging.error(f"Connection error: {e}")
        await interaction.followup.send(f"接続中にエラーが発生しました: {e}")
        return None


# 設定の保存を試み、エラーが発生した場合はログに記録します。
def try_save_style_settings():
    try:
        save_style_settings()
    except IOError as e:
        logging.error(f"Failed to save settings: {e}")


# ボイスチャンネルに接続する関数
async def connect_to_voice_channel(interaction):
    channel = interaction.user.voice.channel
    voice_client = await channel.connect(self_deaf=True)
    return voice_client


async def welcome_user(server, interaction, voice_client, speaker_settings):
    # 接続成功時の処理
    # 接続メッセージの読み上げ
    welcome_voice = "読み上げを開始します。"

    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)  # コマンド使用者のユーザーID
    user_display_name = interaction.user.display_name  # コマンド使用者の表示名
    text_channel_id = str(interaction.channel_id)  # コマンドを使用したテキストチャンネルID

    # サーバー設定が存在しない場合は初期化
    if guild_id not in speaker_settings:
        speaker_settings[guild_id] = {"text_channel": text_channel_id}
    else:
        # 既にサーバー設定が存在する場合はテキストチャンネルIDを更新
        speaker_settings[guild_id]["text_channel"] = text_channel_id
    try:
        # 設定を保存
        save_style_settings()
    except IOError as e:
        logging.error(f"Failed to save settings: {e}")

    # 通知スタイルIDを取得
    announcement_style_id = speaker_settings.get(guild_id, {}).get(
        "announcement", ANNOUNCEMENT_DEFAULT_STYLE_ID
    )
    # ユーザーのスタイルIDを取得
    user_style_id = speaker_settings.get(
        user_id,
        speaker_settings[guild_id].get("user_default", USER_DEFAULT_STYLE_ID),
    )

    # キャラクターとスタイルの詳細を取得
    announcement_speaker_name, announcement_style_name = get_style_details(
        announcement_style_id
    )
    announcement_character_id, announcement_display_name = get_character_info(
        announcement_speaker_name
    )
    announcement_url = f"{ANNOUNCEMENT_URL_BASE}/{announcement_character_id}/"
    user_speaker_name, user_style_name = get_style_details(user_style_id)
    user_character_id, user_tts_display_name = get_character_info(user_speaker_name)
    user_url = f"{ANNOUNCEMENT_URL_BASE}/{user_character_id}/"

    # 歓迎メッセージを作成
    welcome_message = (
        f"アナウンス音声「[{announcement_display_name}]({announcement_url}) {announcement_style_name}」\n"
        f"{user_display_name}さんのテキスト読み上げ音声「[{user_tts_display_name}]({user_url}) {user_style_name}」"
    )

    # メッセージとスタイルIDをキューに追加し、読み上げ
    await server.text_to_speech(
        voice_client, welcome_voice, announcement_style_id, guild_id
    )
    await interaction.followup.send(welcome_message)
