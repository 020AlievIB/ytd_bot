import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# Video configuration
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB in bytes
SUPPORTED_FORMATS = ['mp4', 'webm'] 