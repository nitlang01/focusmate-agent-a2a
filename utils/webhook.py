
from typing import Any, Dict, Optional
import httpx

TaskResult = Dict[str, Any]

async def send_webhook_notification(
    webhook_url: str,
    result: TaskResult,
    auth: Optional[Dict[str, Any]] = None
):
    """Send result to webhook URL"""
    headers = {"Content-Type": "application/json"}

    if auth and auth.get("schemes") == ["TelexApiKey"]:
        headers["Authorization"] = f"Bearer {auth.get('credentials')}"

    async with httpx.AsyncClient() as client:
        await client.post(
            webhook_url,
            json=result.model_dump(),
            headers=headers
        )
