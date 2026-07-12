from fastapi import FastAPI, Request
import shortuuid
import redis
import uvicorn


app = FastAPI()

@app.post("/")
async def root(request: Request):
    text = await request.body()
    text_after = text.decode("utf-8", errors="ignore")
    uuid = shortuuid.uuid()
    short_uuid = uuid[:4]
    with open(f"paste/paste_{short_uuid}", "w") as f:
        f.write(text_after)
    return text_after