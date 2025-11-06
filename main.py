from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from models.a2a import JSONRPCRequest, JSONRPCResponse
from agents.focus_agent import FocusAgent

load_dotenv()

focus_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global focus_agent
    focus_agent = FocusAgent()
    yield
    focus_agent.sessions.clear()

app = FastAPI(title="FocusMate Agent", version="1.0", lifespan=lifespan)

@app.post("/a2a/focus")
async def a2a_endpoint(request: Request):
    body = await request.json()
    rpc_request = JSONRPCRequest(**body)

    messages = []
    context_id = None
    task_id = None
    config = None

    if rpc_request.method == "message/send":
        messages = [rpc_request.params.message]
        config = rpc_request.params.configuration
    elif rpc_request.method == "execute":
        messages = rpc_request.params.messages
        context_id = rpc_request.params.contextId
        task_id = rpc_request.params.taskId

    result = await focus_agent.process_messages(
        messages=messages, context_id=context_id, task_id=task_id, config=config
    )

    return JSONRPCResponse(id=rpc_request.id, result=result).model_dump()

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "focusmate"}
