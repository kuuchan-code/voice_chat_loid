import requests


def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # ステータスコードが200以外の場合は例外を発生させる
        return response.json()  # JSONデータをPythonの辞書として返す
    except requests.RequestException as e:
        print(f"リクエスト中にエラーが発生しました: {e}")
        return None
