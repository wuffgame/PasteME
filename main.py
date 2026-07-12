from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import shortuuid
import redis
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(docs_url=None, redoc_url=None)
redis_url = os.getenv("REDIS_URL")
r = redis.Redis.from_url(str(redis_url), decode_responses=True)

@app.post("/")
async def root(request: Request):
    text = await request.body()
    text_after = text.decode("utf-8", errors="ignore")
    uuid = shortuuid.uuid()
    short_uuid = uuid[:8]
    if not text_after.strip():
        return Response(f"Error: You cannot submit an empty paste.", media_type="text/plain")
    r.set(short_uuid, text_after, ex=86400)
    return Response(f"http://127.0.0.1:8000/{short_uuid}", media_type="text/plain")

@app.get("/linux", response_class=PlainTextResponse)
async def linux():
    return "cat file_name.log | curl --data-binary @- http://127.0.0.1:8000/"

@app.get("/windows", response_class=PlainTextResponse)
async def windows():
    return "(Get-Content file_name.log | Invoke-RestMethod -Uri 'http://127.0.0.1:8000/' -Method Post).Content"
@app.get("/", response_class=PlainTextResponse)
async def home():
    #TODO linux command
    return (
        "===PasteME - originex.tech - CLI Pastebin===\n"
        "How to use on Windows (PowerShell)?\n"
        "Get-Content file_name.log | Invoke-RestMethod -Uri 'http://127.0.0.1:8000/' -Method Post\n"
        'Or use "(Invoke-WebRequest -Uri "http://127.0.0.1:8000/windows" -Method Get).Content" in PowerShell to see command\n\n'
        "How to use on Linux (Bash)?\n"
        "cat file_name.log | curl --data-binary @- http://127.0.0.1:8000/\n"
    )
@app.get("/{id}", response_class=PlainTextResponse)
async def get_paste(id: str):
    try:
        text = r.get(id)
        if text is None:
            return Response("The paste has expired or never existed.", status_code=404)
        return text
    except Exception as e:
        return f"Error: {e}"

