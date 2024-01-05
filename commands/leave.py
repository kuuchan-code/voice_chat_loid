import discord


async def leave(interaction: discord.Interaction, server, speaker_settings):
    # ボイスクライアントが存在するか確認
    if interaction.guild.voice_client:
        guild_id = str(interaction.guild_id)
        await server.clear_playback_queue(guild_id)  # キューをクリア
        if "text_channel" in speaker_settings.get(guild_id, {}):
            del speaker_settings[guild_id]["text_channel"]
        await interaction.guild.voice_client.disconnect()  # 切断
        await interaction.response.send_message("ボイスチャンネルから切断しました。")