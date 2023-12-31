import requests
import re
import json


def fetch_character_infos(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text

        # characterInfos変数の内容を抽出
        match = re.search(
            r"export const characterInfos:.*?=\s*(\{.*?\n\})", data, re.DOTALL
        )
        if match:
            character_infos_js = match.group(1)

            # JavaScriptのオブジェクトキーをJSONのキーに変換する（二重引用符で囲む）
            character_infos_json = re.sub(r"(\w+):", r'"\1":', character_infos_js)

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
