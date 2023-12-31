import aiohttp
import logging

async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"リクエスト中にエラーが発生しました: {e}")
            return None
