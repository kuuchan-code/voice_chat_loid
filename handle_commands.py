import logging
from style_utils import get_current_style_details, update_style_setting
from settings import CHARACTORS_INFO
from utils import validate_style_id

from voice_utils import get_character_info


async def handle_voice_config_command(interaction, style_id: int, voice_scope: str):
    guild_id = str(interaction.guild_id)
    user_id = str(interaction.user.id)
    user_display_name = interaction.user.display_name  # Corrected variable name

    # Define descriptions for each voice style scope
    voice_scope_description = {
        "user": f"{user_display_name}さんのテキスト読み上げ音声",  # Corrected variable name
        "announcement": "アナウンス音声",
        "user_default": "ユーザーデフォルトTTS音声",
    }

    try:
        # If style_id and voice_scope are None, display all settings
        if style_id is None and voice_scope is None:
            messages = []
            for t in voice_scope_description:
                style_id, speaker_name, style_name = get_current_style_details(
                    guild_id, user_id, t
                )
                character_id, display_name = get_character_info(speaker_name)
                url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
                messages.append(
                    f"**{voice_scope_description[t]}**: [{display_name}]({url}) {style_name}"
                )
            await interaction.response.send_message("\n".join(messages))
            return
        elif style_id is None and voice_scope is not None:
            # Display current style settings
            current_style_id, speaker_name, style_name = get_current_style_details(
                guild_id, user_id, voice_scope
            )
            # もち子さんの場合、特別なクレジット表記を使用
            if speaker_name == "もち子さん":
                speaker_name = "もち子(cv 明日葉よもぎ)"
            character_id = CHARACTORS_INFO.get(speaker_name, "unknown")  # キャラクターIDを取得
            url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
            await interaction.response.send_message(
                f"現在の{voice_scope_description[voice_scope]}は「[VOICEVOX:{speaker_name}]({url}) {style_name}」です。"
            )
        elif style_id is not None and voice_scope is None:
            messages = []
            for t in voice_scope_description:
                style_id, speaker_name, style_name = get_current_style_details(
                    guild_id, user_id, t
                )
                character_id, display_name = get_character_info(speaker_name)
                url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
                messages.append(
                    f"**{voice_scope_description[t]}**: [{display_name}]({url}) {style_name}"
                )
            await interaction.response.send_message("\n".join(messages))
            return
        elif style_id is not None and voice_scope is not None:
            valid, speaker_name, style_name = validate_style_id(style_id)
            if not valid:
                await interaction.response.send_message(
                    f"スタイルID {style_id} は無効です。`/list`で有効なIDを確認し、正しいIDを入力してください。",
                    ephemeral=True,
                )
                return
            update_style_setting(guild_id, user_id, style_id, voice_scope)
            # もち子さんの場合、特別なクレジット表記を使用
            if speaker_name == "もち子さん":
                speaker_name = "もち子(cv 明日葉よもぎ)"
            character_id = CHARACTORS_INFO.get(speaker_name, "unknown")  # キャラクターIDを取得
            url = f"https://voicevox.hiroshiba.jp/dormitory/{character_id}/"
            await interaction.response.send_message(
                f"{voice_scope_description[voice_scope]}が「[VOICEVOX:{speaker_name}]({url}) {style_name}」に更新されました。"
            )
            return

    except Exception as e:
        logging.error(f"Error handling voice config command: {e}")
    await interaction.response.send_message(f"エラーが発生しました: {e}")
