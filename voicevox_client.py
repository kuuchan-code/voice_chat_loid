import json
import aiohttp
import requests
import logging
logging.basicConfig(level=logging.DEBUG)

from settings import AUDIO_QUERY_URL, SYNTHESIS_URL


def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"リクエスト中にエラーが発生しました: {e}")
        return None



async def audio_query(text, style_id):
    query_payload = {"text": text, "speaker": style_id}
    headers = {"Content-Type": "application/json"}

    # リクエスト詳細をログに記録
    logging.debug(f"Sending audio query with payload: {query_payload}")

    async with aiohttp.ClientSession() as session:
        logging.debug(f"POST URL: {AUDIO_QUERY_URL}")
        logging.debug(f"Headers: {headers}")
        logging.debug(f"Payload: {query_payload}")

        async with session.post(
            AUDIO_QUERY_URL, headers=headers, data=json.dumps(query_payload)  # jsonパラメータを使用
        ) as response:
            logging.debug(f"Response Status: {response.status}")
            logging.debug(f"Response Headers: {response.headers}")
            if response.status == 200:
                response_data = await response.json()
                logging.debug(f"Response Data: {response_data}")
                return response_data
            else:
                error_detail = await response.text()
                logging.error(f"Error in audio_query: {error_detail}")
                return None




async def synthesis(style_id, query_data):
    # 音声合成を行います。
    synth_payload = {"speaker": style_id}
    headers = {"Content-Type": "application/json", "Accept": "audio/wav"}
    async with aiohttp.ClientSession() as session:
        post_data = json.dumps(query_data)
        logging.debug(f"POST URL: {SYNTHESIS_URL}")
        logging.debug(f"Headers: {headers}")
        logging.debug(f"Payload: {post_data}")

        async with session.post(
            SYNTHESIS_URL,
            headers=headers,
            params=synth_payload,
            data=post_data,
        ) as response:
            logging.debug(f"Response Status: {response.status}")
            logging.debug(f"Response Headers: {response.headers}")
            if response.status == 200:
                return await response.read()
            else:
                error_detail = await response.text()
                logging.error(f"Error in synthesis: {error_detail}")
                return None
