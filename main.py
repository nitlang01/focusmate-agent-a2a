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
            context_id=rpc_request.params.configuration.get("context_id"),
            task_id=rpc_request.params.configuration.get("task_id"),
            config=rpc_request.params.configuration,
        )

        response = JSONRPCResponse(
            jsonrpc="2.0",
            id=rpc_request.id,
            result={"status": "completed", "output": result}
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

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "focusmate"}



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
