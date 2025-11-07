from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import asyncio
import httpx

from models.a2a import JSONRPCRequest, JSONRPCResponse
from agents.focus_agent import FocusAgent
from utils.errors import create_error_response, A2AErrorCode
from utils.webhook import send_webhook_notification

load_dotenv()

focus_agent = None


# ✅ Initialize and cleanup FocusAgent
@asynccontextmanager
async def lifespan(app: FastAPI):
    global focus_agent
    focus_agent = FocusAgent()
    yield
    focus_agent.sessions.clear()


app = FastAPI(title="FocusMate Agent", version="1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "healthy", "agent": "focusmate"}


@app.post("/a2a/focus")
async def handle_focus_request(request: Request):
    """
    Handles all A2A focus requests:
    - Supports JSON-RPC 2.0
    - Supports async webhook callbacks
    - Provides structured error responses
    """
    try:
        body = await request.json()
        rpc_request = JSONRPCRequest(**body)
        webhook_url = rpc_request.params.get("webhookUrl")

        messages = []
        context_id = None
        task_id = None
        config = None

        # Handle different A2A methods
        if rpc_request.method == "message/send":
            messages = [rpc_request.params.message]
            config = rpc_request.params.configuration
        elif rpc_request.method == "execute":
            messages = rpc_request.params.messages
            context_id = rpc_request.params.contextId
            task_id = rpc_request.params.taskId

        # If async webhook is provided, process in background
        if webhook_url:
            asyncio.create_task(process_with_webhook(webhook_url, messages, context_id, task_id, config))
            return JSONResponse(
                status_code=202,
                content={
                    "jsonrpc": "2.0",
                    "id": rpc_request.id,
                    "result": {"status": "accepted", "message": "Focus session started asynchronously"},
                },
            )

        # Otherwise, run normally and return immediate result
        result = await focus_agent.process_messages(
            messages=messages, context_id=context_id, task_id=task_id, config=config
        )
        return JSONRPCResponse(id=rpc_request.id, result=result).model_dump()

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                request_id=body.get("id", None) if "body" in locals() else None,
                code=A2AErrorCode.INTERNAL_ERROR,
                message=str(e),
            ),
        )


async def process_with_webhook(webhook_url, messages, context_id, task_id, config):
    """Background focus task that sends its result to a webhook"""
    try:
        result = await focus_agent.process_messages(
            messages=messages, context_id=context_id, task_id=task_id, config=config
        )
        await send_webhook_notification(webhook_url, {"status": "completed", "output": result})
    except Exception as e:
        await send_webhook_notification(webhook_url, {"status": "failed", "error": str(e)})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
