"""muse-browser REST API (FastAPI).

Run:  python -m server.api
Env:  MUSEBROWSER_TOKEN (bearer), MUSEBROWSER_HOST, MUSEBROWSER_PORT,
      MUSEBROWSER_HOME (profiles + history root), MUSEBROWSER_HEADLESS
"""
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from core import config
from core.engine import BrowserEngine
from core.history import HistoryLog
from core.permissions import PermissionGate

app = FastAPI(title="muse-browser", version="0.1.0")
engine = BrowserEngine(history=HistoryLog(), gate=PermissionGate())


def _auth(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing bearer token")
    if authorization.removeprefix("Bearer ").strip() != config.API_TOKEN:
        raise HTTPException(403, "bad token")


class SessionReq(BaseModel):
    profile: str = "default"
    actor: str = "agent"


class NavigateReq(BaseModel):
    url: str
    actor: str = "agent"


class ClickReq(BaseModel):
    selector: str
    actor: str = "agent"


class TypeReq(BaseModel):
    selector: str
    text: str
    actor: str = "agent"


class EvalReq(BaseModel):
    js: str
    actor: str = "agent"


@app.post("/v1/sessions")
async def create_session(req: SessionReq, authorization: Optional[str] = Header(None)):
    _auth(authorization)
    sid = await engine.create_session(req.profile, req.actor)
    return {"session_id": sid, "profile": req.profile}


@app.delete("/v1/sessions/{sid}")
async def close_session(sid: str, authorization: Optional[str] = Header(None)):
    _auth(authorization)
    await engine.close_session(sid)
    return {"ok": True}


@app.post("/v1/sessions/{sid}/navigate")
async def navigate(sid: str, req: NavigateReq, authorization: Optional[str] = Header(None)):
    _auth(authorization)
    try:
        result, _ = await engine.navigate(sid, req.url, req.actor)
    except PermissionError as e:
        raise HTTPException(403, str(e))
    return {"ok": True, "result": result}


@app.post("/v1/sessions/{sid}/click")
async def click(sid: str, req: ClickReq, authorization: Optional[str] = Header(None)):
    _auth(authorization)
    try:
        result, _ = await engine.click(sid, req.selector, req.actor)
    except PermissionError as e:
        raise HTTPException(403, str(e))
    return {"ok": True, "result": result}


@app.post("/v1/sessions/{sid}/type")
async def type_text(sid: str, req: TypeReq, authorization: Optional[str] = Header(None)):
    _auth(authorization)
    try:
        result, _ = await engine.type(sid, req.selector, req.text, req.actor)
    except PermissionError as e:
        raise HTTPException(403, str(e))
    return {"ok": True, "result": result}


@app.get("/v1/sessions/{sid}/text")
async def page_text(sid: str, authorization: Optional[str] = Header(None)):
    _auth(authorization)
    result, _ = await engine.text(sid)
    return {"ok": True, "text": result}


@app.get("/v1/sessions/{sid}/screenshot")
async def screenshot(sid: str, authorization: Optional[str] = Header(None)):
    _auth(authorization)
    shot, _ = await engine.screenshot(sid)
    return Response(content=shot, media_type="image/png")


@app.post("/v1/sessions/{sid}/evaluate")
async def evaluate(sid: str, req: EvalReq, authorization: Optional[str] = Header(None)):
    _auth(authorization)
    result, _ = await engine.evaluate(sid, req.js, req.actor)
    return {"ok": True, "result": result}


@app.get("/v1/history")
async def history(profile: Optional[str] = None, action: Optional[str] = None,
                  since: Optional[float] = None, limit: int = 200,
                  authorization: Optional[str] = Header(None)):
    _auth(authorization)
    return {"entries": engine.history.query(profile, action, since, limit)}


@app.get("/v1/profiles")
async def profiles(authorization: Optional[str] = Header(None)):
    _auth(authorization)
    return {"profiles": sorted(p.name for p in config.PROFILES_DIR.iterdir() if p.is_dir())}


@app.get("/healthz")
async def healthz():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.api:app", host=config.API_HOST, port=config.API_PORT)
