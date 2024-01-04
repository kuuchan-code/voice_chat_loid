from settings import SPEAKERS_URL
from common_resources import load_style_settings
from core_utils import fetch_json

speakers = fetch_json(SPEAKERS_URL)
speaker_settings = load_style_settings()
