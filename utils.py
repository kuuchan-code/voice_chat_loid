import logging
import pickle
import requests
import jaconv
import re
import discord
from settings import (
    CHARACTORS_INFO,
    DORMITORY_URL_BASE,
    USER_DEFAULT_STYLE_ID,
    ANNOUNCEMENT_DEFAULT_STYLE_ID,
    BotSettings,
    VoiceVoxSettings,
    CONFIG_PICKLE_FILE,
)
import emoji  # 絵文字の判定を行うためのライブラリ


class VoiceSynthConfig:
    def __init__(self):
        self.speakers = fetch_json(VoiceVoxSettings.SPEAKERS_URL)
        self.config_pickle = load_style_settings()

    def validate_style_id(self, style_id):
        valid_style_ids = [
            style["id"] for speaker in self.speakers for style in speaker["styles"]
        ]
        if style_id in valid_style_ids:
            speaker_name, style_name = self.get_style_details(style_id)
            return True, speaker_name, style_name
        return False, None, None

    def get_style_details(self, style_id, default_name="デフォルト"):
        """スタイルIDに対応するスピーカー名とスタイル名を返します。"""
        for speaker in self.speakers:
            for style in speaker["styles"]:
                if style["id"] == style_id:
                    speaker_name = speaker["name"]
                    return (speaker_name, style["name"])
        return (default_name, default_name)

    def save_style_settings(self):
        """スタイル設定を保存します。"""
        with open(CONFIG_PICKLE_FILE, "wb") as f:  # wbモードで開く
            pickle.dump(self.config_pickle, f)  # config_pickleをpickleで保存

    async def handle_voice_state_update(self, server, bot, member, before, after):
        guild_id = member.guild.id
        # ボット自身の状態変更を無視
        if member == bot.user:
            return

        # ボットが接続しているボイスチャンネルを取得
        voice_client = member.guild.voice_client

        # ボットがボイスチャンネルに接続していなければ何もしない
        if not voice_client or not voice_client.channel:
            return

        if (
            before.channel != voice_client.channel
            and after.channel == voice_client.channel
        ):
            announcement_voice = f"{member.display_name}さんが入室しました。"
            # ユーザーのスタイルIDを取得
            user_style_id = self.config_pickle.get(
                member.id,
                self.config_pickle[guild_id].get("user_default", USER_DEFAULT_STYLE_ID),
            )
            user_speaker_name, user_style_name = self.get_style_details(user_style_id)
            user_character_id, user_display_name = get_character_info(user_speaker_name)
            # user_url = f"{DORMITORY_URL_BASE}//{user_character_id}/"
            announcement_message = f"{member.display_name}さん専用の読み上げ音声: [{user_display_name}] - {user_style_name}"

            # テキストチャンネルを取得してメッセージを送信
            text_channel_id = self.config_pickle[guild_id].get("text_channel")
            if text_channel_id:
                text_channel = bot.get_channel(text_channel_id)
                if text_channel:
                    await text_channel.send(announcement_message)
            announcement_style_id = self.config_pickle[guild_id].get(
                "announcement", ANNOUNCEMENT_DEFAULT_STYLE_ID
            )
            await server.text_to_speech(
                voice_client, announcement_voice, announcement_style_id, guild_id
            )

        # ボイスチャンネルから切断したとき
        elif (
            before.channel == voice_client.channel
            and after.channel != voice_client.channel
        ):
            announcement_voice = f"{member.display_name}さんが退室しました。"
            announcement_style_id = self.config_pickle.get(member.guild.id, {}).get(
                "announcement", ANNOUNCEMENT_DEFAULT_STYLE_ID
            )
            await server.text_to_speech(
                voice_client, announcement_voice, announcement_style_id, guild_id
            )

        # ボイスチャンネルに誰もいなくなったら自動的に切断します。
        if after.channel is None and member.guild.voice_client:
            # ボイスチャンネルにまだ誰かいるか確認します。
            if not any(not user.bot for user in before.channel.members):
                # キューをクリアする
                await server.clear_playback_queue(guild_id)
                if (
                    guild_id in self.config_pickle
                    and "text_channel" in self.config_pickle[guild_id]
                ):
                    # テキストチャンネルIDの設定をクリア
                    del self.config_pickle[guild_id]["text_channel"]
                    self.save_style_settings()  # 変更を保存
                    logging.info(f"テキストチャンネルの設定をクリアしました: サーバーID {guild_id}")
                await member.guild.voice_client.disconnect()

    async def handle_message(self, server, message):
        guild_id = message.guild.id

        # 早期リターンを利用してネストを減らす
        if not self.should_process_message(message, guild_id):
            return

        # メッセージ処理
        try:
            message_content = await replace_content(message.content, message)
            if message_content.strip():
                await server.text_to_speech(
                    message.guild.voice_client,
                    message_content,
                    self.get_style_id(message.author.id, guild_id),
                    guild_id,
                )
            if message.attachments:
                await self.announce_file_post(server, message)
        except Exception as e:
            logging.error(f"Error in handle_message: {e}")  # ロギング改善の余地あり

    async def announce_file_post(self, server, message):
        """ファイル投稿をアナウンスします。"""
        file_message = "ファイルを投稿しました。"
        guild_id = message.guild.id
        await server.text_to_speech(
            message.guild.voice_client,
            file_message,
            self.get_style_id(message.author.id, guild_id),
            guild_id,
        )

    def should_process_message(self, message, guild_id):
        """メッセージが処理対象かどうかを判断します。"""
        voice_client = message.guild.voice_client
        allowed_text_channel_id = self.config_pickle.get(guild_id, {}).get(
            "text_channel"
        )
        return (
            voice_client
            and voice_client.channel
            and message.author.voice
            and message.author.voice.channel == voice_client.channel
            and not message.content.startswith(BotSettings.BOT_PREFIX)
            and message.channel.id == allowed_text_channel_id
        )

    def get_style_id(self, user_id, guild_id):
        """ユーザーまたはギルドのスタイルIDを取得します。"""
        return self.config_pickle.get(
            user_id,
            self.config_pickle[guild_id].get("user_default", USER_DEFAULT_STYLE_ID),
        )

    def update_style_setting(self, guild_id, user_id, style_id, voice_scope):
        # Ensure the guild_id exists in the config_pickle
        if guild_id not in self.config_pickle:
            self.config_pickle[guild_id] = {}

        # Ensure the specific voice_scope exists for this guild
        if voice_scope not in self.config_pickle[guild_id]:
            self.config_pickle[guild_id][voice_scope] = {}
        if voice_scope == "user_default":
            self.config_pickle[guild_id]["user_default"] = style_id
        elif voice_scope == "announcement":
            self.config_pickle[guild_id]["announcement"] = style_id
        elif voice_scope == "user":
            self.config_pickle[user_id] = style_id
        self.save_style_settings()


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


def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        logging.error(f"Request error: {err}")
        return None  # Noneを返すことで、呼び出し元でエラーハンドリングを行えるようにする


def load_style_settings():
    """スタイル設定をロードします。"""
    try:
        with open(CONFIG_PICKLE_FILE, "rb") as f:  # rbモードで開く
            return pickle.load(f)  # ファイルからpickleオブジェクトをロード
    except (FileNotFoundError, pickle.UnpicklingError):
        return {}  # ファイルが見つからないか、pickle読み込みエラーの場合は空の辞書を返す


async def replace_content(text, message):
    # ユーザーメンションを検出する正規表現パターン
    user_mention_pattern = re.compile(r"<@!?(\d+)>")
    # ロールメンションを検出する正規表現パターン
    role_mention_pattern = re.compile(r"<@&(\d+)>")
    # チャンネルを検出する正規表現パターン
    channel_pattern = re.compile(r"<#(\d+)>")
    # カスタム絵文字を検出する正規表現パターン
    custom_emoji_pattern = re.compile(r"<:(\w*):\d*>")
    # URLを検出する正規表現パターン
    url_pattern = re.compile(r"https?://\S+")

    def replace_user_mention(match):
        user_id = int(match.group(1))
        user = message.guild.get_member(user_id)
        return user.display_name + "さん" if user else match.group(0)

    def replace_role_mention(match):
        role_id = int(match.group(1))
        role = discord.utils.get(message.guild.roles, id=role_id)
        return role.name + "役職" if role else match.group(0)

    def replace_channel_mention(match):
        channel_id = int(match.group(1))
        channel = message.guild.get_channel(channel_id)
        return channel.name + "チャンネル" if channel else match.group(0)

    def replace_custom_emoji_name_to_kana(match):
        emoji_name = match.group(1)
        return jaconv.alphabet2kana(emoji_name) + " "

    # ユーザーメンションを「○○さん」に置き換え
    text = user_mention_pattern.sub(replace_user_mention, text)
    # ロールメンションを「○○役職」に置き換え
    text = role_mention_pattern.sub(replace_role_mention, text)
    text = channel_pattern.sub(replace_channel_mention, text)
    text = url_pattern.sub("URL省略", text)
    text = custom_emoji_pattern.sub(replace_custom_emoji_name_to_kana, text)
    text = emoji.demojize(text, language="ja")

    return text

def create_config_view(interaction, voice_scope_description):
    view = View()
    for voice_scope, label in voice_scope_description.items():
        button = create_scope_button(interaction, label, voice_scope)
        view.add_item(button)
    return view

def create_scope_button(interaction, label, voice_scope):
    button = Button(
        style=discord.ButtonStyle.primary
        if voice_scope == "user"
        else discord.ButtonStyle.secondary,
        label=label,
    )
    button.callback = create_button_callback(interaction, button, voice_scope)
    return button

def create_button_callback(interaction, button, voice_scope):
    async def on_button_click(interaction: discord.Interaction):
        await initiate_speaker_paging(interaction, voice_scope)
    return on_button_click

class PagingView(discord.ui.View):
    def __init__(self, speakers, voice_scope):
        super().__init__()
        self.speakers = speakers
        self.voice_scope = voice_scope
        self.current_page = 0

    @discord.ui.button(label="<<", style=discord.ButtonStyle.blurple)
    async def first_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = 0
        await self.update_speaker_list(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page > 0:
            self.current_page -= 1
        else:
            self.current_page = len(self.speakers) - 1
        await self.update_speaker_list(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page < len(self.speakers) - 1:
            self.current_page += 1
        else:
            self.current_page = 0
        await self.update_speaker_list(interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.blurple)
    async def last_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = len(self.speakers) - 1
        await self.update_speaker_list(interaction)

    async def update_speaker_list(self, interaction: discord.Interaction):
        self.first_button.disabled = self.current_page == 0
        self.last_button.disabled = self.current_page == len(self.speakers) - 1
        voice_scope_description = get_voice_scope_description(interaction)
        # 'interaction'を正しく使ってメッセージを編集
        speaker_name = self.speakers[self.current_page]["name"]
        content = f"矢印ボタンで使用するキャラクターを選択し、スタイルを選んでください：\nページ {self.current_page + 1} / {len(self.speakers)}\n"
        speaker_character_id, speaker_display_name = get_character_info(
            speaker_name
        )
        speaker_url = f"{DORMITORY_URL_BASE}/{speaker_character_id}/"

        # 歓迎メッセージを作成
        content += f"[{speaker_display_name}]({speaker_url})"
        # 古いスタイルのボタンを削除して新しいものを追加
        self.clear_items()

        # ナビゲーションボタンを追加
        self.add_item(self.first_button)
        self.add_item(self.previous_button)
        self.add_item(self.next_button)
        self.add_item(self.last_button)

        # 現在の話者の各スタイルに対応するボタンを追加
        for style in self.speakers[self.current_page]["styles"]:
            style_button = discord.ui.Button(
                label=style["name"], style=discord.ButtonStyle.secondary
            )

            # ボタンが押されたときの処理を定義
            async def handle_style_button_click(
                interaction: discord.Interaction,
                button: discord.ui.Button,
                style_id=style["id"],
            ):
                await on_style_button_click(interaction, button, style_id)

            async def on_style_button_click(
                interaction: discord.Interaction,
                button: Button,
                style_id,
            ):
                # スタイル変更をここで処理
                valid, speaker_name, style_name = voice_config.validate_style_id(
                    style_id
                )
                if not valid:
                    await interaction.response.edit_message(
                        f"スタイルID {style_id} は無効です。`/list`で有効なIDを確認し、正しいIDを入力してください。",
                        view=self,
                    )
                voice_config.update_style_setting(
                    interaction.guild.id,
                    interaction.user.id,
                    style_id,
                    self.voice_scope,
                )
                speaker_character_id, speaker_display_name = get_character_info(
                    speaker_name
                )
                speaker_url = f"{DORMITORY_URL_BASE}/{speaker_character_id}/"
                await interaction.response.send_message(
                    f"{voice_scope_description[self.voice_scope]}が「[{speaker_display_name}]({speaker_url}) {style_name}」に更新されました。"
                )

            # Capture the current button and style_id using default arguments
            style_button.callback = (
                lambda interaction, button=style_button, style_id=style[
                    "id"
                ]: asyncio.create_task(
                    handle_style_button_click(interaction, button, style_id)
                )
            )

            self.add_item(style_button)
        await interaction.response.edit_message(content=content, view=self)

async def initiate_speaker_paging(interaction: discord.Interaction, voice_scope):
    voice_scope_description = get_voice_scope_description(interaction)
    # 初期ページングビューを作成
    view = PagingView(voice_config.speakers, voice_scope)

    # 最初の話者を表示
    speaker_name = (
        voice_config.speakers[0]["name"]
        if voice_config.speakers
        else "利用可能な話者がいません"
    )
    content = f"矢印ボタンで使用するキャラクターを選択し、スタイルを選んでください：\nページ 1 / {len(voice_config.speakers)}\n"
    speaker_character_id, speaker_display_name = get_character_info(speaker_name)
    speaker_url = f"{DORMITORY_URL_BASE}/{speaker_character_id}/"

    content += f"[{speaker_display_name}]({speaker_url})"
    # 最初の話者の各スタイルに対応するボタンを追加
    for style in voice_config.speakers[0]["styles"]:  # 'styles'は各話者のスタイル辞書のリストと仮定
        style_button = discord.ui.Button(
            label=style["name"], style=discord.ButtonStyle.secondary
        )

        # Define an async function for handling button clicks
        async def handle_style_button_click(
            interaction: discord.Interaction,
            button: discord.ui.Button,
            style_id=style["id"],
        ):
            await on_style_button_click(interaction, button, style_id)

        # ボタンが押されたときの処理を定義（別の関数を定義することも検討してください）
        async def on_style_button_click(
            interaction: discord.Interaction,
            button: Button,
            style_id=style["id"],
        ):
            # スタイル変更をここで処理
            valid, speaker_name, style_name = voice_config.validate_style_id(
                style_id
            )
            if not valid:
                await interaction.response.edit_message(
                    f"スタイルID {style_id} は無効です。`/list`で有効なIDを確認し、正しいIDを入力してください。",
                    view=view,
                )
            voice_config.update_style_setting(
                interaction.guild.id, interaction.user.id, style_id, voice_scope
            )
            speaker_character_id, speaker_display_name = get_character_info(
                speaker_name
            )
            speaker_url = f"{DORMITORY_URL_BASE}/{speaker_character_id}/"
            await interaction.response.send_message(
                f"{voice_scope_description[voice_scope]}が「[{speaker_display_name}]({speaker_url}) {style_name}」に更新されました。"
            )

        # Replace the existing 'style_button.callback' assignment with the following:
        style_button.callback = (
            lambda interaction, button=style_button, style_id=style[
                "id"
            ]: asyncio.create_task(
                handle_style_button_click(interaction, button, style_id)
            )
        )
        # 最初のページで<<と<ボタンを無効化
        view.first_button.disabled = True
        view.add_item(style_button)
    await interaction.response.edit_message(content=content, view=view)

def get_voice_scope_description(interaction):
        return {
            "user": f"{interaction.user.display_name}さん専用の読み上げ音声",
            "announcement": "入退出時のアナウンス音声",
            "user_default": "未設定ユーザーの読み上げ音声",
        }