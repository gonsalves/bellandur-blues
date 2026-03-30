from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_DIR / "audio"
DATA_DIR = BASE_DIR / "data"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'bellandur.db'}"

TTS_VOICE = os.getenv("TTS_VOICE", "en-US-AndrewMultilingualNeural")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

AUDIO_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
