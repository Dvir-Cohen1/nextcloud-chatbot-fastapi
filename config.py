import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("NEXTCLOUD_BOT_SECRET")
NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
