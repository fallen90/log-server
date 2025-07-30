from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio
import os

LOG_DIR = "/mnt/data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

app = FastAPI()
log_queue = asyncio.Queue()

async def writer_task():
    while True:
        entry = await log_queue.get()
        log_line = f"[{entry['timestamp']}] [{entry['source']}] {entry['log']}\n"
        log_path = os.path.join(LOG_DIR, f"{datetime.utcnow().strftime('%Y-%m-%d')}.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
                f.flush()
        except Exception as e:
            print(f"Log write failed: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(writer_task())

@app.post("/log")
async def receive_log(request: Request):
    try:
        body = await request.body()
        program = request.headers.get("X-Program", "unknown")
        await log_queue.put({
            "source": program,
            "timestamp": datetime.utcnow().isoformat(),
            "log": body.decode("utf-8", errors="replace").strip()
        })
        return {"status": "queued"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/tail")
async def tail_logs(lines: int = 50):
    try:
        log_path = os.path.join(LOG_DIR, f"{datetime.utcnow().strftime('%Y-%m-%d')}.log")
        with open(log_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            size = 0
            block = []
            while end > 0 and len(block) < lines:
                size = min(1024, end)
                end -= size
                f.seek(end)
                block = (f.read(size) + b"".join(block)).splitlines()[-lines:]
            return [line.decode("utf-8", errors="replace") for line in block]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/search")
async def search_logs(q: str):
    results = []
    log_path = os.path.join(LOG_DIR, f"{datetime.utcnow().strftime('%Y-%m-%d')}.log")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if q.lower() in line.lower():
                    results.append(line.strip())
        return results
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/logs")
async def list_logs():
    return sorted(os.listdir(LOG_DIR))

