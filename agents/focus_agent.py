import time
import asyncio
from uuid import uuid4
from typing import List, Optional, Dict
from datetime import datetime

from models.a2a import (
    A2AMessage, TaskResult, TaskStatus, Artifact, MessagePart, MessageConfiguration
)
from utils.redis_client import redis_client

class FocusAgent:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}

    async def process_messages(
        self,
        messages: List[A2AMessage],
        context_id: Optional[str] = None,
        task_id: Optional[str] = None,
        config: Optional[MessageConfiguration] = None
    ) -> TaskResult:
        context_id = context_id or str(uuid4())
        task_id = task_id or str(uuid4())

        user_message = messages[-1]
        text = user_message.parts[0].text.strip().lower()

        if text.startswith("/focus start"):
            result_msg = await self.start_session(context_id, text)
        elif text.startswith("/focus stop"):
            result_msg = await self.stop_session(context_id)
        elif text.startswith("/focus stats"):
            result_msg = await self.get_stats(context_id)
        else:
            result_msg = "💡 Try `/focus start <minutes> <task>` or `/focus stop` or `/focus stats`"

        response_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=result_msg)],
            taskId=task_id
        )

        return TaskResult(
            id=task_id,
            contextId=context_id,
            status=TaskStatus(state="completed", message=response_message),
            artifacts=[
                Artifact(
                    name="focus-response",
                    parts=[MessagePart(kind="text", text=result_msg)]
                )
            ],
            history=messages + [response_message]
        )

    async def start_session(self, context_id: str, text: str) -> str:
        parts = text.split(" ")
        if len(parts) < 4:
            return "⚠️ Usage: `/focus start <minutes> <task>`"

        try:
            duration = int(parts[2])
        except ValueError:
            return "⚠️ Duration must be an integer (minutes)."

        task = " ".join(parts[3:])
        start_time = int(time.time())

        session = {
            "task": task,
            "duration": duration,
            "start_time": start_time,
        }
        self.sessions[context_id] = session
        await redis_client.set(context_id, str(session))

        return f"🚀 Focus session started for {duration} minutes on '{task}'. Stay focused!"

    async def stop_session(self, context_id: str) -> str:
        session = self.sessions.pop(context_id, None)
        if not session:
            return "⚠️ No active focus session found."

        elapsed = (int(time.time()) - session["start_time"]) // 60
        await redis_client.delete(context_id)

        return f"🛑 Focus session stopped. You focused on '{session['task']}' for {elapsed} minutes."

    async def get_stats(self, context_id: str) -> str:
        active = await redis_client.get(context_id)
        if not active:
            return "📊 No active sessions right now."
        return f"📊 Current session: {active}"

if not redis_client:
    print("⚠️ Redis not initialized, skipping cache")
