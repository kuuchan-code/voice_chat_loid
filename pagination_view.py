import discord
from discord.ui import View, Button
from settings import ITEMS_PER_PAGE

from utils import get_character_info

def update_pagination_buttons(view, total_pages):
    view.children[0].disabled = view.page <= 1
    view.children[1].disabled = view.page >= total_pages

# ページネーションのビュークラス
class PaginationView(View):
    """A view for paginating through a list of speakers."""

    def __init__(self, speakers, page=1):
        super().__init__()
        self.speakers = speakers
        self.page = page
        self.total_pages = max(
            1,
            len(speakers) // ITEMS_PER_PAGE
            + (1 if len(speakers) % ITEMS_PER_PAGE > 0 else 0),
        )

    @discord.ui.button(label="前へ", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.page = max(1, self.page - 1)
        await self.update_message(interaction)

    @discord.ui.button(label="次へ", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.page = min(self.total_pages, self.page + 1)
        await self.update_message(interaction)

    async def update_message(self, interaction):
        # 現在のページに応じてボタンの有効/無効を設定
        update_pagination_buttons(self, self.total_pages)

        start_index = (self.page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE

        # メッセージを更新
        message = f"**利用可能な話者とスタイル (ページ {self.page}/{self.total_pages}):**\n"
        for speaker in self.speakers[start_index:end_index]:
            name = speaker["name"]
            character_id, display_name = get_character_info(name)
            url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
            styles_info = " ".join(
                f"{style['name']} (ID: `{style['id']}`)" for style in speaker["styles"]
            )
            message += f"\n[{display_name}]({url}): {styles_info}"

        if interaction.response.is_done():
            await interaction.followup.edit_message(
                message_id=interaction.message.id, content=message, view=self
            )
        else:
            await interaction.response.edit_message(content=message, view=self)

    async def send_initial_message(self, interaction):
        update_pagination_buttons(self, self.total_pages)
        start_index = (self.page - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE

        # メッセージを整形して作成
        message = f"**利用可能な話者とスタイル (ページ {self.page}):**\n"
        for speaker in self.speakers[start_index:end_index]:
            name = speaker["name"]
            character_id, display_name = get_character_info(name)
            url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
            styles_info = " ".join(
                f"{style['name']} (ID: `{style['id']}`)" for style in speaker["styles"]
            )
            message += f"\n[{display_name}]({url}): {styles_info}"

        # 最初のメッセージを送信
        await interaction.response.send_message(
            content=message,
            view=self,
            ephemeral=True,
        )
