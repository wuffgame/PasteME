from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import shortuuid
import redis
import uvicorn


app = FastAPI()

@app.post("/")
async def root(request: Request):
    text = await request.body()
    text_after = text.decode("utf-8", errors="ignore")
    uuid = shortuuid.uuid()
    short_uuid = uuid[:8]
    with open(f"paste/paste_{short_uuid}", "w") as f:
        f.write(text_after)
    return f"http://127.0.0.1:8000/{short_uuid}"

@app.get("/{id}", response_class=PlainTextResponse)
async def get_paste(id: str):
    try:
        with open(f"paste/paste_{id}", "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"