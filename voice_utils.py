
import asyncio
from settings import CHARACTORS_INFO
from voice import get_guild_playback_queue


def get_character_info(speaker_name):
    # もち子さんの特別な処理
    if speaker_name == "もち子さん":
        character_key = "もち子さん"  # CHARACTORS_INFOでのキー
        display_name = "VOICEVOX:もち子(cv 明日葉よもぎ)"  # 特別な表示名
    else:
        character_key = speaker_name  # その他のスピーカーは通常通り処理
        display_name = f"VOICEVOX:{speaker_name}"  # 標準の表示名

    character_id = CHARACTORS_INFO.get(character_key, "unknown")  # キャラクターIDを取得
    return character_id, display_name




async def clear_playback_queue(guild_id):
    guild_queue = get_guild_playback_queue(guild_id)
    while not guild_queue.empty():
        try:
            guild_queue.get_nowait()
        except asyncio.QueueEmpty:
            continue
        guild_queue.task_done()

async def text_to_speech(voice_client, text, style_id, guild_id):
    """テキストを音声に変換して再生します。"""
    if not voice_client or not voice_client.is_connected():
        return  # 接続されていない場合は処理を中断

    try:
        lines = text.split("\n")
        for line in filter(None, lines):  # 空行を除外
            guild_queue = get_guild_playback_queue(guild_id)
            await guild_queue.put((voice_client, line, style_id))
    except Exception as e:
        print(f"Error in text_to_speech: {e}")


