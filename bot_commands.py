import logging
import discord
from settings import (
    APPROVED_GUILD_OBJECTS,
    ERROR_MESSAGES,
)
from utils import (
    VoiceSynthConfig,
    create_config_view,
    get_voice_scope_description,
)
from voice import VoiceSynthServer
from discord.ext import commands


logging.basicConfig(level=logging.INFO)


def setup_leave_command(bot, server, voice_config):
    # ボットをボイスチャンネルから切断するコマンド
    @bot.tree.command(
        name="leave", guilds=APPROVED_GUILD_OBJECTS, description="ボットをボイスチャンネルから切断します。"
    )
    async def leave(interaction: discord.Interaction):
        # ボイスクライアントが存在しない場合、何もせずに終了
        if not interaction.guild.voice_client:
            await interaction.response.send_message("ボットはボイスチャンネルに接続されていません。")
            return

        guild_id = interaction.guild_id
        # キューをクリア
        await server.clear_playback_queue(guild_id)

        # テキストチャンネル設定を削除
        if "text_channel" in voice_config.config_pickle.get(guild_id, {}):
            del voice_config.config_pickle[guild_id]["text_channel"]
        voice_config.save_style_settings()

        # ボイスクライアントを切断
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("ボイスチャンネルから切断しました。")


def setup_join_command(bot, server, voice_config):
    # ボットをボイスチャンネルに接続するコマンド
    @bot.tree.command(
        name="join",
        guilds=APPROVED_GUILD_OBJECTS,
        description="ボットをボイスチャンネルに接続し、読み上げを開始します。",
    )
    async def join(interaction: discord.Interaction):
        # defer the response to keep the interaction alive
        await interaction.response.defer()
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send(ERROR_MESSAGES["connection"])
        try:
            voice_client = await connect_to_voice_channel(interaction)
            await welcome_user(server, interaction, voice_client, voice_config)
        except discord.ClientException as e:
            logging.error(f"Connection error: {e}")
            await interaction.followup.send(f"接続中にエラーが発生しました: {e}")


def setup_config_command(bot, voice_config):
    @bot.tree.command(
        name="config", guilds=APPROVED_GUILD_OBJECTS, description="読み上げ音声を設定します。"
    )
    async def config(interaction: discord.Interaction):
        voice_scope_description = get_voice_scope_description(interaction)
        view = create_config_view(interaction, voice_scope_description)
        await interaction.response.send_message(
            "設定対象を選んでください：", view=view, ephemeral=True
        )


def setup_info_command(bot, voice_config):
    @bot.tree.command(
        name="info",
        guilds=APPROVED_GUILD_OBJECTS,
        description="現在の読み上げ音声スコープと設定を表示します。",
    )
    async def info(interaction: discord.Interaction):
        guild_id = interaction.guild_id

        # サーバーの設定を取得
        guild_settings = voice_config.config_pickle.get(guild_id, {})
        text_channel_id = guild_settings.get("text_channel", "未設定")

        style_ids = get_style_ids(guild_id, interaction.user.id, voice_config)
        speaker_details = get_speaker_details(voice_config, *style_ids)
        info_message = create_info_message(
            interaction, text_channel_id, speaker_details
        )

        # ユーザーに設定の詳細を表示
        await interaction.response.send_message(info_message, ephemeral=True)


def setup_commands(
    server: VoiceSynthServer, bot: commands.Bot, voice_config: VoiceSynthConfig
):
    setup_join_command(bot, server, voice_config)
    setup_leave_command(bot, server, voice_config)
    setup_config_command(bot, voice_config)
    setup_info_command(bot, voice_config)
