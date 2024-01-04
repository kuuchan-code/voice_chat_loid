import discord
from discord import app_commands
from handle_commands import handle_voice_config_command
from pagination_view import PaginationView
from settings import (
    APPROVED_GUILD_IDS,
)
from speaker_selection_view import SpeakerSelectionView
from voice import connect_voice_client, disconnect_voice_client
from shared_resources import speakers



def setup_commands(bot):
    @bot.tree.command(
        name="leave", guilds=APPROVED_GUILD_IDS, description="ボットをボイスチャンネルから切断します。"
    )
    async def leave(interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await disconnect_voice_client(interaction)

    @bot.tree.command(
        name="voice_config",
        guilds=APPROVED_GUILD_IDS,
        description="あなたのテキスト読み上げキャラクターを設定します。",
    )
    async def voice_config(interaction: discord.Interaction, style_id: int):
        await handle_voice_config_command(interaction, style_id, voice_scope="user")

    @bot.tree.command(
        name="server_voice_config",
        guilds=APPROVED_GUILD_IDS,
        description="サーバーのテキスト読み上げキャラクターを表示また設定します。",
    )
    @app_commands.choices(
        voice_scope=[
            app_commands.Choice(name="アナウンス音声", value="announcement"),
            app_commands.Choice(name="ユーザーデフォルトTTS音声", value="user_default"),
        ]
    )
    async def server_voice_config(
        interaction: discord.Interaction, voice_scope: str, style_id: int = None
    ):
        await handle_voice_config_command(interaction, style_id, voice_scope)

    @bot.tree.command(
        name="join",
        guilds=APPROVED_GUILD_IDS,
        description="ボットをボイスチャンネルに接続し、読み上げを開始します。",
    )
    async def join(interaction: discord.Interaction):
        await connect_voice_client(interaction)
    @bot.tree.command(
        name="list", guilds=APPROVED_GUILD_IDS, description="話者とそのスタイルをページングして表示します。"
    )
    async def list(interaction: discord.Interaction):
        if not speakers:
            await interaction.response.send_message("話者のデータを取得できませんでした。")
            return

        # 最初のページを表示
        view = PaginationView(speakers)
        await view.send_initial_message(interaction)

    @bot.tree.command(
        name="select_speaker", guilds=APPROVED_GUILD_IDS, description="話者を選択します。"
    )
    async def select_speaker(interaction: discord.Interaction):
        if not speakers:
            await interaction.response.send_message("話者のデータを取得できませんでした。")
            return

        # 話者選択のためのページネーションビューを作成
        view = SpeakerSelectionView(speakers)
        await view.send_initial_message(interaction)

    @bot.tree.command(
        name="help", guilds=APPROVED_GUILD_IDS, description="利用可能なコマンドとその説明を表示します。"
    )
    async def help_command(interaction: discord.Interaction):
        help_text = """
        **VOICECHATLOIDヘルプ**
        以下は利用可能なコマンドのリストです：

        `/join` - ボットをユーザーのいるボイスチャンネルに接続します。
        `/leave` - ボットをボイスチャンネルから切断します。
        `/voice_config [style_id]` - ユーザーのテキスト読み上げ音声スタイルを設定します。
        `/server_voice_config [voice_scope] [style_id]` - サーバーのテキスト読み上げキャラクターを設定します。
        `/list` - 利用可能な話者とそのスタイルを表示します。

        各コマンドの詳細については、コマンドを入力時に表示される説明を参照してください。
        """
        await interaction.response.send_message(help_text)
