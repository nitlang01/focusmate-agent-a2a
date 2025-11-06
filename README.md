# 🧠 FocusMate AI (A2A Agent)

An AI-powered productivity companion for Telex users.  
Built using **FastAPI + A2A protocol** to manage focus sessions.

## 🚀 Features
- `/focus start <minutes> <task>` — start a focus timer  
- `/focus stop` — stop your current session  
- `/focus stats` — view current session details  

## ⚙️ Run Locally
```bash
pip install -e .
uvicorn main:app --host 0.0.0.0 --port 5001
