"""Drive muse-browser directly through the engine (no HTTP server needed)."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import BrowserEngine
from core.history import HistoryLog
from core.permissions import PermissionGate


async def main():
    engine = BrowserEngine(history=HistoryLog(), gate=PermissionGate())
    sid = await engine.create_session(profile="demo")
    print("session:", sid)

    result, _ = await engine.navigate(sid, "https://example.com")
    print(result)

    result, _ = await engine.text(sid)
    print("page text (first 300 chars):", result[:300])

    # Permission gate demo: account-creation URL is hard-denied
    try:
        await engine.navigate(sid, "https://example.com/signup")
    except PermissionError as e:
        print("gate correctly denied:", e)

    # Show the history
    for e in engine.history.query(profile="demo"):
        print(f"[{e['iso']}] {e['action']} -> {str(e['result'])[:80]}")

    await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
