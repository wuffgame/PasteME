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
    r.set(short_uuid, text_after, ex=86400)
    if not text_after.strip():
        return Response(f"Error: You cannot submit an empty paste.", media_type="text/plain")
    return Response(f"http://127.0.0.1:8000/{short_uuid}", media_type="text/plain")

@app.get("/{id}", response_class=PlainTextResponse)
async def get_paste(id: str):
    try:
        text = r.get(id)
        if text is None:
            return Response("The paste has expired or never existed.", status_code=404, media_type="text/plain")
        return text
    except Exception as e:
        return f"Error: {e}"