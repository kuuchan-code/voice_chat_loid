import discord
from discord import app_commands
from handle_commands import handle_voice_config_command
from pagination_view import PaginationView
from settings import (
    APPROVED_GUILD_IDS,
    USER_DEFAULT_STYLE_ID,
    ANNOUNCEMENT_DEFAULT_STYLE_ID,
)
from speaker_selection_view import SpeakerSelectionView
from utils import (
    get_character_info,
    speakers,
    speaker_settings,
    save_style_settings,
    get_style_details,
)
from voice import disconnect_voice_client, text_to_speech
from style_utils import update_style_setting, get_current_style_details


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
