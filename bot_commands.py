import asyncio
import discord
from settings import (
    CHARACTORS_INFO,
    SPEAKERS_ENDPOINT,
    TEST_GUILD_ID,
    USER_DEFAULT_STYLE_ID,
    NOTIFY_DEFAULT_STYLE_ID,
)
from voicevox_client import fetch_json


def setup_commands(bot):
    speakers_data = fetch_json(SPEAKERS_ENDPOINT)

    @bot.tree.command(
        name="list", guild=TEST_GUILD_ID, description="スピーカーとそのスタイルIDを表示します。"
    )
    async def list(interaction: discord.Interaction):
        """スピーカーとそのスタイルIDを表示します。"""
        if not speakers_data:
            await interaction.response.send_message("スピーカーのデータを取得できませんでした。")
            return

        # メッセージを整形して作成
        message = "**利用可能なスピーカーとスタイル:**\n"
        for speaker in speakers_data:
            name = speaker["name"]
            character_id = CHARACTORS_INFO.get(name, "unknown")  # キャラクターIDを取得
            url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
            styles = ", ".join(
                [f"{style['name']} (ID: {style['id']})" for style in speaker["styles"]]
            )
            message += f"\n[{name}]({url}): {styles}"

        await interaction.response.send_message(message)

    @bot.tree.command(name="join", guild=TEST_GUILD_ID)
    async def join(interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message(f"{channel.name}に接続しました。")
        else:
            await interaction.response.send_message("あなたはボイスチャンネルにいません。")
