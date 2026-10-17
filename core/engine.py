"""Browser engine: Playwright + persistent Chromium profiles.

The core primitive is launch_persistent(): Chromium with a real user-data
directory on disk, so cookies / localStorage / sessions survive restarts.
"""
import uuid
from pathlib import Path

from . import config
from .history import HistoryLog
from .permissions import PermissionGate


class BrowserEngine:
    def __init__(self, history: HistoryLog | None = None,
                 gate: PermissionGate | None = None):
        self.history = history or HistoryLog()
        self.gate = gate or PermissionGate()
        self._pw = None
        self._sessions: dict[str, dict] = {}  # session_id -> {profile, context, page}

    async def _ensure_pw(self):
        if self._pw is None:
            from playwright.async_api import async_playwright
            self._pw = await async_playwright().start()
        return self._pw

    def profile_dir(self, profile: str) -> Path:
        d = config.PROFILES_DIR / profile
        d.mkdir(parents=True, exist_ok=True)
        meta = d / "meta.json"
        if not meta.exists():
            import json, time
            meta.write_text(json.dumps({
                "name": profile,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            }))
        return d

    async def create_session(self, profile: str = "default", actor: str = "agent") -> str:
        pw = await self._ensure_pw()
        context = await pw.chromium.launch_persistent_context(
            str(self.profile_dir(profile)),
            headless=config.HEADLESS,
            accept_downloads=True,
        )
        page = context.pages[0] if context.pages else await context.new_page()
        sid = uuid.uuid4().hex[:12]
        self._sessions[sid] = {"profile": profile, "context": context, "page": page}
        self.history.record(profile, sid, "session_create", {}, "persistent context launched", actor)
        return sid

    async def close_session(self, session_id: str, actor: str = "agent"):
        s = self._sessions.pop(session_id, None)
        if s:
            await s["context"].close()
            self.history.record(s["profile"], session_id, "session_close", {}, "context closed", actor)

    def _get(self, session_id: str):
        s = self._sessions.get(session_id)
        if not s:
            raise KeyError(f"unknown session: {session_id}")
        return s

    async def _act(self, session_id: str, action: str, params: dict, actor: str = "agent"):
        s = self._get(session_id)
        profile = s["profile"]
        decision = self.gate.check(profile, action, params)
        if not decision.allowed:
            self.history.record(profile, session_id, action, params,
                                f"DENIED: {decision.reason}", actor)
            raise PermissionError(decision.reason)
        page = s["page"]
        if action == "navigate":
            await page.goto(params["url"], wait_until="domcontentloaded", timeout=30000)
            result = f"navigated to {params['url']} | title: {await page.title()}"
        elif action == "click":
            await page.click(params["selector"], timeout=15000)
            result = f"clicked {params['selector']}"
        elif action == "type":
            await page.fill(params["selector"], params["text"], timeout=15000)
            result = f"typed into {params['selector']} ({len(params['text'])} chars)"
        elif action == "text":
            result = (await page.inner_text("body"))[:8000]
        elif action == "screenshot":
            shot = await page.screenshot(full_page=False)
            result = f"screenshot {len(shot)} bytes"
            return shot, "screenshot"
        elif action == "evaluate":
            val = await page.evaluate(params["js"])
            result = str(val)[:4000]
        else:
            raise ValueError(f"unknown action: {action}")
        self.history.record(profile, session_id, action, params, result[:500], actor)
        return result, "text"

    # Convenience wrappers
    async def navigate(self, sid, url, actor="agent"):
        return await self._act(sid, "navigate", {"url": url}, actor)

    async def click(self, sid, selector, actor="agent"):
        return await self._act(sid, "click", {"selector": selector}, actor)

    async def type(self, sid, selector, text, actor="agent"):
        return await self._act(sid, "type", {"selector": selector, "text": text}, actor)

    async def text(self, sid, actor="agent"):
        return await self._act(sid, "text", {}, actor)

    async def screenshot(self, sid, actor="agent"):
        return await self._act(sid, "screenshot", {}, actor)

    async def evaluate(self, sid, js, actor="agent"):
        return await self._act(sid, "evaluate", {"js": js}, actor)

    async def shutdown(self):
        for sid in list(self._sessions):
            await self.close_session(sid)
        if self._pw:
            await self._pw.stop()
            self._pw = None
