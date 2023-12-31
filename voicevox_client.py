import requests
import logging

def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"リクエスト中にエラーが発生しました: {e}")
        return None
