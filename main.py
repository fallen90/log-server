from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
import os

LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

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
        finally:
            log_queue.task_done()

@asynccontextmanager
async def lifespan(app: FastAPI):
    writer = asyncio.create_task(writer_task())
    yield
    writer.cancel()
    try:
        await writer
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

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
        
        # Check if file exists
        if not os.path.exists(log_path):
            return []
        
        # Read the file and get the last N lines
        with open(log_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            return [line.strip() for line in all_lines[-lines:]]
            
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/search")
async def search_logs(q: str):
    results = []
    log_path = os.path.join(LOG_DIR, f"{datetime.utcnow().strftime('%Y-%m-%d')}.log")
    try:
        # Check if file exists
        if not os.path.exists(log_path):
            return []
            
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if q.lower() in line.lower():
                    results.append(line.strip())
        return results
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/logs")
async def list_logs():
    try:
        return sorted([f for f in os.listdir(LOG_DIR) if f.endswith('.log')])
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
