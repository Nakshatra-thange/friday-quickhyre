from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile  # noqa: E402
from fastapi.responses import StreamingResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from app.agent import run_turn  # noqa: E402
from app.llm import budget_ok  # noqa: E402
from app.models import ChatRequest  # noqa: E402
from app.resume import ResumeError, extract_text, parse_resume  # noqa: E402
from app.search import get_store  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("friday.api")

MAX_UPLOAD = 2 * 1024 * 1024
MAX_SESSIONS = 500
app = FastAPI(title="Friday (prototype)")
SESSIONS: dict[str, dict] = {}  # in-memory only: resumes never touch disk
HITS: dict[str, deque] = defaultdict(deque)


@app.on_event("startup")
def _warm() -> None:
    get_store()


def _ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() or (request.client.host if request.client else "unknown")


def _rate_limit(ip: str) -> None:
    limit = int(os.getenv("RATE_LIMIT_PER_MIN", "10"))
    now = time.time()
    q = HITS[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(429, "Too many requests. Please slow down a little.")
    q.append(now)


def _session(sid: str) -> dict:
    if sid not in SESSIONS and len(SESSIONS) >= MAX_SESSIONS:
        SESSIONS.pop(next(iter(SESSIONS)))  # drop the oldest session (and its resume)
    return SESSIONS.setdefault(sid, {"messages": [], "resume": None, "resume_text": None, "layout": {}})


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request) -> StreamingResponse:
    _rate_limit(_ip(request))
    session = _session(req.session_id)

    async def gen():
        async for ev in run_turn(session, req.message):
            yield f"data: {json.dumps(ev)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/upload")
async def upload(request: Request, session_id: str = Form(...), file: UploadFile = File(...)) -> dict:
    _rate_limit(_ip(request))
    if not 8 <= len(session_id) <= 64:
        raise HTTPException(400, "Bad session id.")
    if not budget_ok():
        raise HTTPException(429, "Friday's daily demo budget is used up. Please try again tomorrow.")
    data = await file.read(MAX_UPLOAD + 1)
    if len(data) > MAX_UPLOAD:
        raise HTTPException(413, "File too large (max 2 MB).")
    try:
        text, layout = extract_text(file.filename or "", data)
    except ResumeError as e:
        raise HTTPException(400, str(e))
    profile = await parse_resume(text)
    s = _session(session_id)
    s.update(resume=profile.model_dump(), resume_text=text, layout=layout)
    log.info(json.dumps({"event": "resume_loaded", "skills": len(profile.skills),
                         "suspicious": profile.suspicious}))  # counts only, no content
    return {"skills": profile.skills, "years_experience": profile.years_experience,
            "suspicious": profile.suspicious}


app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")