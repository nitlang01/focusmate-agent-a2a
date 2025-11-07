# Example: async focus task
import asyncio
from dataclasses import dataclass
from fastapi import FastAPI, Request
from utils.webhook import send_webhook_notification

app = FastAPI()

@dataclass
class TaskResult:
    status: str
    output: str

@app.post("/a2a/focus")
async def handle_focus_request(request: Request):
    payload = await request.json()
    webhook_url = payload["params"].get("webhookUrl")

    # Start async background job
    asyncio.create_task(run_focus_session(webhook_url))
    return {"status": "accepted", "message": "Focus session started asynchronously"}

async def run_focus_session(webhook_url):
    # simulate work
    await asyncio.sleep(10)
    result = TaskResult(status="completed", output="Focus session done!")
    await send_webhook_notification(webhook_url, result)
