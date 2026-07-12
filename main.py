from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse, HTMLResponse
import shortuuid
import redis
import os
import markdown
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(docs_url=None, redoc_url=None)
redis_url = os.getenv("REDIS_URL")
r = redis.Redis.from_url(str(redis_url), decode_responses=True)

@app.post("/")
async def root(request: Request):
    ip = request.client.host
    if r.get(ip) == "True":
        return Response("Error: You have a active cooldown (30s).\n", status_code=429, media_type="text/plain")
    text = await request.body()
    ttl = request.headers.get("X-TTL", 86400)
    try:
        ttl = int(ttl)
        if ttl > 86400:
            return "The maximum expiration time is 24 hours (86400s)."
    except ValueError:
        ttl = 86400
    if len(text) > 2 * 1024 * 1024:
        return "Error: Paste size limits exceeded (Max 2MB).\n"
    text_after = text.decode("utf-8", errors="ignore")
    uuid = shortuuid.uuid()
    short_uuid = uuid[:8]
    if not text_after.strip():
        return Response(f"Error: You cannot submit an empty paste.", media_type="text/plain")
    r.set(short_uuid, text_after, ex=ttl)
    r.set(ip, "True", ex=30)
    return Response(f"Your paste link: http://127.0.0.1:8000/{short_uuid})", media_type="text/plain")

@app.get("/linux", response_class=PlainTextResponse)
async def linux():
    return "cat file | curl --data-binary @- http://originex.tech"

@app.get("/powershell", response_class=PlainTextResponse)
async def powershell():
    return '(Get-Content file | Invoke-WebRequest -Uri "http://originex.tech" -Method Post).Content'

@app.get("/cmd", response_class=PlainTextResponse)
async def cmd():
    return 'curl --data-binary @file http://originex.tech'

@app.get("/macos", response_class=PlainTextResponse)
async def macos():
    return 'cat file | curl --data-binary @- http://originex.tech'
@app.get("/", response_class=PlainTextResponse)
async def home(request: Request):
    try:
        with open("MAIN.md", "r", encoding="utf-8") as f:
            md_content = f.read()

        with open("index.html", "r") as file:
            html = file.read()

        user_agent = request.headers.get("user-agent", "").lower()

        if any(browser in user_agent for browser in ["mozilla", "chrome", "safari", "edge", "opera"]):
            html_content = markdown.markdown(md_content)
            full_html = html.format(html_content=html_content)
            return HTMLResponse(content=full_html)
        return PlainTextResponse("Tutorial available in browser!!! If you from CLI you can use /powershell, /cmd, /linux, /macos")
    except FileNotFoundError:
        return PlainTextResponse("=== PasteME ===\nWelcome! (MAIN.md missing)")

@app.get("/{id}", response_class=PlainTextResponse)
async def get_paste(id: str):
    try:
        text = r.get(id)
        if text is None:
            return Response("The paste has expired or never existed.", status_code=404)
        return text
    except Exception as e:
        return f"Error: {e}"


