import redis.asyncio as redis
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = None  # Start as None


async def init_redis():
    """Initialize Redis connection safely."""
    global redis_client
    redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
    try:
        await redis_client.ping()
        print("✅ Connected to Redis successfully")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
