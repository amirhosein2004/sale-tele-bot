# تنظیمات ربات

import os

BOT_TOKEN = os.environ["BOT_TOKEN"]

USE_PROXY = os.environ.get("USE_PROXY", "false").lower() == "true"

PROXY = None
if USE_PROXY:
    PROXY = {
        "url" : os.environ["PROXY_URL"],
        "username": os.environ.get("USERNAME"),  # if needed
        "password": os.environ.get("PASSWORD")   # if needed
    }


