import aiohttp
import asyncio
import json
import discord
import io
from settings import ANNOUNCEMENT_DEFAULT_STYLE_ID, SYNTHESIS_URL, AUDIO_QUERY_URL, USER_DEFAULT_STYLE_ID
from style_utils import save_style_settings
from utils import get_character_info


# Initialize global variables
guild_playback_queues = {}
headers = {"Content-Type": "application/json"}


def get_guild_playback_queue(guild_id):
    """指定されたギルドIDのplayback_queueを取得または作成します。"""
    if guild_id not in guild_playback_queues:
        guild_playback_queues[guild_id] = asyncio.Queue()
    return guild_playback_queues[guild_id]


async def process_playback_queue(guild_id):
    guild_queue = get_guild_playback_queue(guild_id)
    while True:
        voice_client, line, style_id = await guild_queue.get()
        try:
            if (
                voice_client
                and voice_client.is_connected()
                and not voice_client.is_playing()
            ):
                await speak_line(voice_client, line, style_id, guild_id)
        except Exception as e:
            print(e)  # Log the error or handle it as needed.
        finally:
            guild_queue.task_done()


async def audio_query(text, style_id):
    # 音声合成用のクエリを作成します。
    query_payload = {"text": text, "speaker": style_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            AUDIO_QUERY_URL, headers=headers, params=query_payload
        ) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 422:
                error_detail = await response.text()
                print(f"処理できないエンティティ: {error_detail}")
                return None


async def synthesis(speaker, query_data):
    # 音声合成を行います。
    synth_payload = {"speaker": speaker}
    headers = {"Content-Type": "application/json", "Accept": "audio/wav"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            SYNTHESIS_URL,
            headers=headers,
            params=synth_payload,
            data=json.dumps(query_data),
        ) as response:
            if response.status == 200:
                return await response.read()
            return None


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


async def speak_line(voice_client, line, style_id, guild_id):
    query_data = await audio_query(line, style_id)
    if query_data:
        voice_data = await synthesis(style_id, query_data)
        if voice_data:
            audio_source = discord.FFmpegPCMAudio(io.BytesIO(voice_data), pipe=True)
            voice_client.play(audio_source)

            # Wait for the current audio to finish playing before returning
            while voice_client.is_playing():
                await asyncio.sleep(0.1)


async def disconnect_voice_client(interaction):
    guild_id = str(interaction.guild_id)
    await clear_playback_queue(guild_id)
    if "text_channel" in speaker_settings.get(guild_id, {}):
        del speaker_settings[guild_id]["text_channel"]
    await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message("ボイスチャンネルから切断しました。")


async def connect_voice_client(interaction):
        # defer the response to keep the interaction alive
    await interaction.response.defer()

    try:
        if interaction.user.voice and interaction.user.voice.channel:
            channel = interaction.user.voice.channel
            voice_client = await channel.connect(self_deaf=True)
            # 接続成功時の処理
            # 接続メッセージの読み上げ
            welcome_voice = "読み上げを開始します。"

            guild_id = str(interaction.guild_id)
            user_id = str(interaction.user.id)  # コマンド使用者のユーザーID
            user_display_name = (
                interaction.user.display_name
            )  # Corrected variable name
            text_channel_id = str(interaction.channel_id)  # このコマンドを使用したテキストチャンネルID

            # サーバー設定が存在しない場合は初期化
            if guild_id not in speaker_settings:
                speaker_settings[guild_id] = {"text_channel": text_channel_id}
            else:
                # 既にサーバー設定が存在する場合はテキストチャンネルIDを更新
                speaker_settings[guild_id]["text_channel"] = text_channel_id

            save_style_settings()  # 変更を保存

            # 通知スタイルIDを取得
            announcement_style_id = speaker_settings.get(guild_id, {}).get(
                "announcement", ANNOUNCEMENT_DEFAULT_STYLE_ID
            )
            # ユーザーのスタイルIDを取得
            user_style_id = speaker_settings.get(
                user_id,
                speaker_settings[guild_id].get(
                    "user_default", USER_DEFAULT_STYLE_ID
                ),
            )

            # クレジットをメッセージに追加
            announcement_speaker_name, announcement_style_name = get_style_details(
                announcement_style_id
            )
            (
                announcement_character_id,
                announcement_display_name,
            ) = get_character_info(announcement_speaker_name)
            announcement_url = f"https://voicevox.hiroshiba.jp/dormitory/{announcement_character_id}/"
            user_speaker_name, user_style_name = get_style_details(user_style_id)
            user_character_id, user_tts_display_name = get_character_info(
                user_speaker_name
            )
            user_url = (
                f"https://voicevox.hiroshiba.jp/dormitory/{user_character_id}/"
            )
            welcome_message = (
                f"アナウンス音声「[{announcement_display_name}]({announcement_url}) {announcement_style_name}」\n"
                f"{user_display_name}さんのテキスト読み上げ音声「[{user_tts_display_name}]({user_url}) {user_style_name}」"
            )

            # メッセージとスタイルIDをキューに追加
            await text_to_speech(
                voice_client, welcome_voice, announcement_style_id, guild_id
            )
            await interaction.followup.send(welcome_message)
        else:
            await interaction.followup.send(
                "ボイスチャンネルに接続できませんでした。ユーザーがボイスチャンネルにいることを確認してください。"
            )
    except Exception as e:
        # エラーメッセージをユーザーに通知
        await interaction.followup.send(f"接続中にエラーが発生しました: {e}")


async def clear_playback_queue(guild_id):
    guild_queue = get_guild_playback_queue(guild_id)
    while not guild_queue.empty():
        try:
            guild_queue.get_nowait()
        except asyncio.QueueEmpty:
            continue
        guild_queue.task_done()
