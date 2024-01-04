import requests
import jaconv
import re
import discord
from settings import (
    BOT_PREFIX,
    USER_DEFAULT_STYLE_ID,
    ANNOUNCEMENT_DEFAULT_STYLE_ID,
)
from style_utils import save_style_settings
from voice_utils import get_character_info
from shared_resources import speakers, speaker_settings
from core_utils import fetch_json
from settings import CHARACTORS_INFO


current_voice_client = None


def validate_style_id(style_id):
    valid_style_ids = [
        style["id"] for speaker in speakers for style in speaker["styles"]
    ]
    if style_id in valid_style_ids:
        speaker_name, style_name = get_style_details(style_id)
        return True, speaker_name, style_name
    return False, None, None




async def replace_content(text, message):
    # Define patterns for mentions, channels, emojis, and URLs
    patterns = {
        "user_mention": re.compile(r"<@!?(\d+)>"),
        "role_mention": re.compile(r"<@&(\d+)>"),
        "channel": re.compile(r"<#(\d+)>"),
        "custom_emoji": re.compile(r"<:(\w*):\d*>"),
        "url": re.compile(r"https?://\S+"),
    }

    # Replacement functions for each pattern type
    def replace_mention_with_name(match, context, format_str):
        entity_id = int(match.group(1))
        entity = context.get(entity_id)
        return format_str.format(entity) if entity else match.group(0)

    def replace_channel_mention(match, message):
        channel_id = int(match.group(1))
        channel = message.guild.get_channel(channel_id)
        return channel.name + "チャンネル" if channel else match.group(0)

    def replace_custom_emoji_name_to_kana(match):
        emoji_name = match.group(1)
        return jaconv.alphabet2kana(emoji_name) + " "

    # Replace content based on patterns
    text = patterns["user_mention"].sub(
        lambda m: replace_mention_with_name(m, message.guild.get_member, "{}さん"), text
    )
    text = patterns["role_mention"].sub(
        lambda m: replace_mention_with_name(
            m, discord.utils.get(message.guild.roles, id=int(m.group(1))), "{}役職"
        ),
        text,
    )
    text = patterns["channel"].sub(lambda m: replace_channel_mention(m, message), text)
    text = patterns["url"].sub("URL省略", text)
    text = patterns["custom_emoji"].sub(replace_custom_emoji_name_to_kana, text)
    text = replace_keywords_with_short_name(text, emoji_ja, special_cases)

    return text


def replace_keywords_with_short_name(text, symbol_dict, special_cases):
    for symbol, data in symbol_dict.items():
        if symbol in special_cases:
            text = text.replace(symbol, special_cases[symbol])
            continue
        text = text.replace(symbol, data["short_name"])
    return text


async def handle_voice_state_update(bot, member, before, after):
    guild_id = str(member.guild.id)
    # ボット自身の状態変更を無視
    if member == bot.user:
        return

    # ボットが接続しているボイスチャンネルを取得
    voice_client = member.guild.voice_client

    # ボットがボイスチャンネルに接続していなければ何もしない
    if not voice_client or not voice_client.channel:
        return

    if before.channel != voice_client.channel and after.channel == voice_client.channel:
        announcement_voice = f"{member.display_name}さんが入室しました。"
        # ユーザーのスタイルIDを取得
        user_style_id = speaker_settings.get(str(member.id), USER_DEFAULT_STYLE_ID)
        user_speaker_name, user_style_name = get_style_details(user_style_id)
        user_character_id, user_display_name = get_character_info(user_speaker_name)
        user_url = f"https://voicevox.hiroshiba.jp/dormitory/{user_character_id}/"
        announcement_message = f"{member.display_name}さんのテキスト読み上げ音声「[{user_display_name}]({user_url}) {user_style_name}」"

        # テキストチャンネルを取得してメッセージを送信
        text_channel_id = speaker_settings[guild_id].get("text_channel")
        if text_channel_id:
            text_channel = bot.get_channel(int(text_channel_id))
            if text_channel:
                await text_channel.send(announcement_message)
        # アナウンス用の音声スタイルIDを取得
        announcement_style_id = speaker_settings.get(guild_id, {}).get(
            "notify", ANNOUNCEMENT_DEFAULT_STYLE_ID
        )
        await text_to_speech(
            voice_client, announcement_voice, announcement_style_id, guild_id
        )

    # ボイスチャンネルから切断したとき
    elif (
        before.channel == voice_client.channel and after.channel != voice_client.channel
    ):
        announcement_voice = f"{member.display_name}さんが退室しました。"
        announcement_style_id = speaker_settings.get(str(member.guild.id), {}).get(
            "announcement", ANNOUNCEMENT_DEFAULT_STYLE_ID
        )
        await text_to_speech(
            voice_client, announcement_voice, announcement_style_id, guild_id
        )

    # ボイスチャンネルに誰もいなくなったら自動的に切断します。
    if after.channel is None and member.guild.voice_client:
        # ボイスチャンネルにまだ誰かいるか確認します。
        if not any(not user.bot for user in before.channel.members):
            # 現在の読み上げを停止する
            if current_voice_client and current_voice_client.is_playing():
                current_voice_client.stop()

            # キューをクリアする
            await clear_playback_queue(guild_id)
            if (
                guild_id in speaker_settings
                and "text_channel" in speaker_settings[guild_id]
            ):
                # テキストチャンネルIDの設定をクリア
                del speaker_settings[guild_id]["text_channel"]
                save_style_settings()  # 変更を保存
                print(f"テキストチャンネルの設定をクリアしました: サーバーID {guild_id}")
            await member.guild.voice_client.disconnect()


# Initialize global variables
guild_playback_queues = {}
emoji_ja = fetch_json(
    "https://raw.githubusercontent.com/yagays/emoji-ja/master/data/emoji_ja.json"
)
# 特別な置き換え規則
special_cases = {"🇵🇸": "パレスチナ"}


async def handle_message(bot, message):
    guild_id = str(message.guild.id)

    # 早期リターンを利用してネストを減らす
    if not should_process_message(message, guild_id):
        return

    # メッセージ処理
    try:
        message_content = await replace_content(message.content, message)
        if message_content.strip():
            await text_to_speech(
                message.guild.voice_client,
                message_content,
                get_style_id(message.author.id, guild_id),
                guild_id,
            )
        if message.attachments:
            await announce_file_post(message)
    except Exception as e:
        print(f"Error in handle_message: {e}")  # ロギング改善の余地あり


def should_process_message(message, guild_id):
    """メッセージが処理対象かどうかを判断します。"""
    voice_client = message.guild.voice_client
    allowed_text_channel_id = speaker_settings.get(guild_id, {}).get("text_channel")
    return (
        voice_client
        and voice_client.channel
        and message.author.voice
        and message.author.voice.channel == voice_client.channel
        and not message.content.startswith(BOT_PREFIX)
        and str(message.channel.id) == allowed_text_channel_id
    )


async def announce_file_post(message):
    """ファイル投稿をアナウンスします。"""
    file_message = "ファイルを投稿しました。"
    guild_id = str(message.guild.id)
    await text_to_speech(
        message.guild.voice_client,
        file_message,
        get_style_id(message.author.id, guild_id),
        guild_id,
    )


def get_style_id(user_id, guild_id):
    """ユーザーまたはギルドのスタイルIDを取得します。"""
    return speaker_settings.get(
        str(user_id),
        speaker_settings[guild_id].get("user_default", USER_DEFAULT_STYLE_ID),
    )


from settings import CHARACTORS_INFO



def get_style_details(style_id, default_name="デフォルト"):
    """スタイルIDに対応するスピーカー名とスタイル名を返します。"""
    for speaker in speakers:
        for style in speaker["styles"]:
            if style["id"] == style_id:
                speaker_name = speaker["name"]
                return (speaker_name, style["name"])
    return (default_name, default_name)
