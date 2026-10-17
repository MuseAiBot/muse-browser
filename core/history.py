"""Append-only, queryable history log. Every browsing action is recorded here."""
import json
import time
from pathlib import Path
from typing import Any, Optional

from . import config


class HistoryLog:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or (config.HISTORY_DIR / "history.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, profile: str, session_id: str, action: str,
               params: dict, result_summary: str = "", actor: str = "agent") -> dict:
        entry = {
            "ts": time.time(),
            "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "profile": profile,
            "session_id": session_id,
            "actor": actor,
            "action": action,
            "params": params,
            "result": result_summary,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def query(self, profile: Optional[str] = None, action: Optional[str] = None,
              since: Optional[float] = None, limit: int = 200) -> list[dict]:
        if not self.path.exists():
            return []
        out = []
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if profile and e.get("profile") != profile:
                    continue
                if action and e.get("action") != action:
                    continue
                if since and e.get("ts", 0) < since:
                    continue
                out.append(e)
        return out[-limit:]
