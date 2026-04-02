import os

import redis
from dotenv import load_dotenv

load_dotenv()
load_dotenv("document-ai-api/.env")

try:
    broker_url = os.getenv("CELERY_BROKER_URL")
    if not broker_url:
        raise ValueError(
            "CELERY_BROKER_URL is not set. Add it to your environment or .env file."
        )

    # Managed Redis often requires SSL; if this fails, change 'redis://' to 'rediss://'.
    r = redis.from_url(broker_url)
    if r.ping():
        print("Connection successful. Redis is ready for Celery tasks.")
except Exception as e:
    print(f"Connection error: {e}")
