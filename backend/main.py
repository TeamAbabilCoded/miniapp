from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import httpx
import urllib.parse

from database import init_db, connect_db, insert_task, get_all_tasks
from config import TELEGRAM_API, BOT_TOKEN, REWARD_POIN_PER_TASK, SAFELINKU_API_KEY

app = FastAPI()
init_db()

# CORS agar bisa diakses dari browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/visit")
async def visit(request: Request, user_id: str, task_id: int, url: str):
    ip = request.client.host
    user_agent = request.headers.get("user-agent")
    now = datetime.utcnow().isoformat()

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM click_logs WHERE user_id=? AND task_id=?", (user_id, task_id))
    if cur.fetchone():
        return JSONResponse({"status": "already_done"})

    cur.execute("INSERT OR IGNORE INTO click_logs (user_id, task_id, timestamp, ip, user_agent) VALUES (?, ?, ?, ?, ?)",
                (user_id, task_id, now, ip, user_agent))
    conn.commit()
    conn.close()

    await send_point(user_id, task_id)
    return RedirectResponse(url)

async def send_point(user_id: str, task_id: int):
    text = f"✅ Kamu telah menyelesaikan tugas #{task_id}!\n+{REWARD_POIN_PER_TASK} poin telah ditambahkan."
    payload = {"chat_id": user_id, "text": text}
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API}/sendMessage", data=payload)

@app.post("/add_task")
async def add_task(name: str = Form(...), url: str = Form(...)):
    short_url = await shorten_safelinku(url)
    insert_task(name, url, short_url)
    return {"message": "Tugas ditambahkan", "shortlink": short_url}

@app.get("/tasks")
async def tasks():
    result = get_all_tasks()
    return [{"id": row[0], "name": row[1], "url": row[2]} for row in result]

async def shorten_safelinku(long_url):
    safelink_url = f"https://safelinku.com/api?api={SAFELINKU_API_KEY}&url={urllib.parse.quote_plus(long_url)}"
    async with httpx.AsyncClient() as client:
        response = await client.get(safelink_url)
        data = response.json()
        return data.get("shortenedUrl")
