from shared_resources import speakers
def get_style_details(style_id, default_name="デフォルト"):
    """スタイルIDに対応するスピーカー名とスタイル名を返します。"""
    for speaker in speakers:
        for style in speaker["styles"]:
            if style["id"] == style_id:
                speaker_name = speaker["name"]
                return (speaker_name, style["name"])
    return (default_name, default_name)
