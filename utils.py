import requests
import re
import json


def fetch_character_infos(url):
    # URLからデータを取得
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text

        # characterInfos変数の内容を抽出
        match = re.search(
            r"export const characterInfos:.*?=\s*(\{.*?\n\})", data, re.DOTALL
        )
        if match:
            # JavaScriptオブジェクトをPython辞書に変換
            character_infos_js = match.group(1)
            # JavaScriptのオブジェクト表記をJSON形式に変換
            character_infos_json = character_infos_js.replace("name", '"name"').replace(
                "id", '"id"'
            )
            # JSONをPythonの辞書に変換
            character_infos = json.loads(character_infos_json)
            return character_infos
    else:
        print("データを取得できませんでした。ステータスコード:", response.status_code)
        return None
