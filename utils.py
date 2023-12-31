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

            # すべてのキーを二重引用符で囲む
            character_infos_json = re.sub(r'(?<!")(\w+)(?!"):', r'"\1":', character_infos_js)

            # 不要なカンマを削除
            character_infos_json = re.sub(r',\s*([}\]])', r'\1', character_infos_json)

            try:
                character_infos = json.loads(character_infos_json)
                return character_infos
            except json.JSONDecodeError as e:
                print(f"JSONデコードエラー: {e}")
                print(character_infos_json)  # エラーが発生したJSONを出力
                # 特定の行を出力して問題を特定
                lines = character_infos_json.split("\n")
                if len(lines) > 56:
                    print("問題のある行:", lines[55])  # 行は0から始まるので56行目は55となる

    else:
        print("データを取得できませんでした。ステータスコード:", response.status_code)
        return None