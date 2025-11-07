from enum import Enum
from typing import Optional, Dict

class A2AErrorCode(Enum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

def create_error_response(
    request_id: str,
    code: A2AErrorCode,
    message: str,
    data: Optional[Dict] = None
):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code.value,
            "message": message,
            "data": data or {}
        }
    }
