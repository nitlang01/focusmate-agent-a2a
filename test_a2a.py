import requests
import json
import sys

URL = "http://127.0.0.1:8000/a2a/focus"

def test_focusmate(command):
    print("📡 Sending request...\n")

    payload = {
        "jsonrpc": "2.0",
        "id": "test-001",
        "method": "message/send",   # ✅ REQUIRED VALUE
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [
                    {"kind": "text", "text": command}
                ],
                "messageId": "msg-001",
                "taskId": "task-001"
            },
            "configuration": {
                "blocking": True   # ✅ Your FocusAgent ignores this anyway
            }
        }
    }

    response = requests.post(URL, json=payload)

    print(f"✅ STATUS: {response.status_code}")
    print("📩 RESPONSE TEXT:\n", response.text)

    try:
        data = response.json()
        print("\n🧩 VALID JSON RESPONSE:\n", json.dumps(data, indent=2))
    except Exception:
        print("\n❌ Invalid JSON returned!")

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "/focus start 30 write documentation"
    test_focusmate(command)
