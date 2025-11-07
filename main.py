from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from models.a2a import JSONRPCRequest, JSONRPCResponse
from agents.focus_agent import FocusAgent
from contextlib import asynccontextmanager
import asyncio
import os

focus_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global focus_agent
    focus_agent = FocusAgent()
    yield
    focus_agent.sessions.clear()

app = FastAPI(title="FocusMate Agent", version="1.0", lifespan=lifespan)

@app.post("/a2a/focus")
async def a2a_focus(request: Request):
    try:
        body = await request.json()
        rpc_request = JSONRPCRequest(**body)

        # process
        result = await focus_agent.process_messages(
            messages=[rpc_request.params.message],
            context_id=getattr(rpc_request.params.configuration, "context_id", None),
            task_id=getattr(rpc_request.params.configuration, "task_id", None),
            config=rpc_request.params.configuration,
        )

        response = JSONRPCResponse(
            jsonrpc="2.0",
            id=rpc_request.id,
            result=result
        )
        return JSONResponse(content=response.model_dump())

    except Exception as e:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            },
            status_code=500
        )

@app.get("/")
def root():
    return {"message": "FocusMate A2A agent active."}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global focus_agent
    focus_agent = FocusAgent()
    yield
    focus_agent.sessions.clear()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    print("⚠️ Error:", exc)
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )

from utils.redis_client import init_redis, redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    global focus_agent
    await init_redis()  # Initialize Redis here before FocusAgent starts
    focus_agent = FocusAgent()
    yield
    focus_agent.sessions.clear()

