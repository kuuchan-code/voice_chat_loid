import requests
import re
import json


def fetch_character_infos(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text

        # characterInfos変数の内容を抽出
        match = re.search(r"export const characterInfos:.*?=\s*(\{.*?\n\})", data, re.DOTALL)
        if match:
            character_infos_js = match.group(1)

            # より堅牢な方法でキーを二重引用符で囲む
            character_infos_json = re.sub(r'([\'"])?([a-zA-Z0-9_]+)([\'"])?:', r'"\2":', character_infos_js)

            # 不要な行末のカンマを削除（JavaScriptでは許容されるが、JSONでは許容されない）
            character_infos_json = re.sub(r',\s*}', '}', character_infos_json)
            character_infos_json = re.sub(r',\s*\]', ']', character_infos_json)

            try:
                # JSONをPythonの辞書に変換
                character_infos = json.loads(character_infos_json)
                return character_infos
            except json.JSONDecodeError as e:
                print(f"JSONデコードエラー: {e}")
                return None
    else:
        print("データを取得できませんでした。ステータスコード:", response.status_code)
        return None