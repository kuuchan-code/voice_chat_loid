import discord
from discord.ui import View
from style_utils import update_style_setting

# スタイル選択のビュークラス
class StyleSelectionView(View):
    """A view for selecting a voice style for a given speaker."""

    def __init__(self, speaker, user_id, guild_id):
        super().__init__()
        self.speaker = speaker
        self.user_id = user_id
        self.guild_id = guild_id
        self.add_style_buttons()

    def add_style_buttons(self):
        # スタイル情報に基づいてボタンを動的に生成
        for style in self.speaker["styles"]:
            style_name = style["name"]
            style_id = style["id"]
            button = discord.ui.Button(
                label=f"{style_name} (ID: {style_id})",
                style=discord.ButtonStyle.secondary,
            )
            button.callback = self.create_button_callback(style_id)
            self.add_item(button)

    def create_button_callback(self, style_id):
        # コールバック関数を動的に生成
        async def button_callback(interaction: discord.Interaction):
            await self.on_select(interaction, style_id)

        return button_callback

    async def on_select(self, interaction: discord.Interaction, style_id: int):
        # スタイル選択時の処理
        style_name = next(
            (
                style["name"]
                for style in self.speaker["styles"]
                if style["id"] == style_id
            ),
            None,
        )
        if not style_name:
            await interaction.response.send_message("選択したスタイルIDが無効です。", ephemeral=True)
            return

        # スタイル設定を更新
        update_style_setting(self.guild_id, self.user_id, style_id, "user")

        # ユーザーに更新を通知
        await interaction.response.send_message(
            f"スタイルが「{self.speaker['name']} - {style_name}」に設定されました。"
        )



