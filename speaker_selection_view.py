import discord
from discord.ui import View
from settings import ITEMS_PER_PAGE
from style_selection_view import StyleSelectionView


# 話者選択のビュークラス
class SpeakerSelectionView(View):
    """A view for selecting a speaker from a list."""

    def __init__(self, speakers, page=1):
        super().__init__()
        self.speakers = speakers
        self.page = page
        self.total_pages = max(
            1,
            len(speakers) // ITEMS_PER_PAGE
            + (1 if len(speakers) % ITEMS_PER_PAGE > 0 else 0),
        )
        self.add_buttons()

    async def send_initial_message(self, interaction):
        message_content = self.create_message_content()
        await interaction.response.send_message(
            content=message_content, view=self, ephemeral=True
        )

    def create_message_content(self):
        start_index = (self.page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE
        message_content = f"**利用可能な話者 (ページ {self.page}/{self.total_pages}):**\n"
        for speaker in self.speakers[start_index:end_index]:
            message_content += f"- {speaker['name']}\n"
        return message_content

    async def update_message(self, interaction):
        # ボタンをクリアして再生成
        self.clear_items()
        self.add_buttons()

        # メッセージを更新
        message_content = self.create_message_content()

        if interaction.response.is_done():
            await interaction.followup.edit_message(
                message_id=interaction.message.id, content=message_content, view=self
            )
        else:
            await interaction.response.edit_message(content=message_content, view=self)

    def add_buttons(self):
        start_index = (self.page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE

        for speaker in self.speakers[start_index:end_index]:
            button = discord.ui.Button(
                label=speaker["name"], style=discord.ButtonStyle.secondary
            )
            button.callback = self.create_button_callback(speaker)
            self.add_item(button)

        # 'Previous' button を作成。
        previous_button = discord.ui.Button(
            label="前へ", style=discord.ButtonStyle.primary
        )
        previous_button.disabled = self.page <= 1
        previous_button.callback = self.on_previous_button_click  # 引数なしで修正

        # 'Next' button を作成。
        next_button = discord.ui.Button(label="次へ", style=discord.ButtonStyle.primary)
        next_button.disabled = self.page >= self.total_pages
        next_button.callback = self.on_next_button_click  # 引数なしで修正

        # Add buttons to the view.
        self.add_item(previous_button)
        self.add_item(next_button)

    async def on_previous_button_click(self, interaction: discord.Interaction):
        self.page = max(1, self.page - 1)
        await self.update_message(interaction)

    async def on_next_button_click(self, interaction: discord.Interaction):
        self.page = min(self.total_pages, self.page + 1)
        await self.update_message(interaction)

    def create_button_callback(self, speaker):
        async def button_callback(interaction: discord.Interaction):
            await self.select_speaker(interaction, speaker)

        return button_callback

    async def select_speaker(self, interaction: discord.Interaction, speaker):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        view = StyleSelectionView(speaker, user_id, guild_id)
        await interaction.response.edit_message(
            content=f"**{speaker['name']}** のスタイルを選択してください。", view=view
        )

