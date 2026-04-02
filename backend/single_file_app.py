import base64
import uuid
import json
import time
import threading
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn

# In-memory task store (simplified single-file example)
TASKS: Dict[str, Dict] = {}

app = FastAPI(title="Document AI - Single File", version="1.0")

class DocumentRequest(BaseModel):
    file_base64: str
    file_type: str

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None

@app.get("/", response_class=HTMLResponse)
def home():
    html = """
<!doctype html>
<html lang='en'>
<head>
  <meta charset='UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1.0' />
  <title>Document AI Single File</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 32px; background:#121212; color:#eee; }
    .card { border:1px solid #444; padding:20px; border-radius:8px; background:#1e1e1e; }
    .btn { padding:10px 16px; margin-top:10px; display:inline-block; color:#fff; background:#0078d4; border:none; border-radius:5px; cursor:pointer; }
    .text { width:100%; min-height:120px; background:#111; color:#eee; border:1px solid #333; border-radius:6px; }
  </style>
</head>
<body>
  <div class='card'>
    <h1>Document AI frontend+backend in one file</h1>
    <p>Upload text or data as base64 and start a job.</p>
    <textarea id='content' class='text' placeholder='Paste plain text, then click run'></textarea>
    <br>
    <button class='btn' onclick='startTask()'>Start Task</button>
    <p id='taskId'>Task ID: <em>-</em></p>
    <p id='status'>Status: <em>-</em></p>
    <pre id='result'></pre>
  </div>
  <script>
    async function startTask() {
      const text = document.getElementById('content').value.trim();
      if (!text) return alert('Enter some text to simulate document data.');
      const b64 = btoa(unescape(encodeURIComponent(text)));

      const resp = await fetch('/api/document-analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_base64: b64, file_type: 'text' }),
      });
      const data = await resp.json();
      document.getElementById('taskId').innerHTML = 'Task ID: <strong>' + data.task_id + '</strong>';
      pollStatus(data.task_id);
    }

    async function pollStatus(taskId) {
      const statusEl = document.getElementById('status');
      const resultEl = document.getElementById('result');

      const timer = setInterval(async () => {
        const resp = await fetch('/api/task/' + taskId);
        const data = await resp.json();
        statusEl.innerHTML = 'Status: <strong>' + data.status + '</strong>';
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(timer);
          resultEl.textContent = JSON.stringify(data.result || { error: 'No result' }, null, 2);
        }
      }, 1000);
    }
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html)

@app.post("/api/document-analyze", response_model=TaskResponse)
def analyze_document(request: DocumentRequest):
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {"status": "queued", "result": None}

    def background_process(task_id: str, req: DocumentRequest):
        try:
            TASKS[task_id]["status"] = "processing"
            # quick simulated work
            time.sleep(2)
            decoded = base64.b64decode(req.file_base64).decode('utf-8', errors='replace')
            summary = decoded.strip().slice(0, 280) if hasattr(decoded.strip(), 'slice') else decoded.strip()
            entities = {"length": len(decoded), "words": len(decoded.split())}

            TASKS[task_id]["status"] = "completed"
            TASKS[task_id]["result"] = {
                "summary": summary,
                "entities": entities,
                "sentiment": "Neutral"
            }
        except Exception as e:
            TASKS[task_id]["status"] = "failed"
            TASKS[task_id]["result"] = {"error": str(e)}

    thread = threading.Thread(target=background_process, args=(task_id, request))
    thread.start()

    return TaskResponse(task_id=task_id, status="queued")

@app.get("/api/task/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    task = TASKS[task_id]
    return TaskResponse(task_id=task_id, status=task["status"], result=task["result"])

if __name__ == "__main__":
    uvicorn.run("single_file_app:app", host="0.0.0.0", port=8000, reload=True)
