"""Session persistence: save/restore browser sessions, manage disk profiles.

Pure stdlib — no downloads. Profiles live under <data_dir>/profiles/<name>/.
"""
import json, os, shutil, time
from pathlib import Path

class SessionStore:
    def __init__(self, data_dir="profiles"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _profile_dir(self, name):
        safe = "".join(c for c in name if c.isalnum() or c in "-_") or "default"
        return self.data_dir / safe

    def create(self, name="default", meta=None):
        """Create (or reattach to) a profile. Returns session descriptor."""
        d = self._profile_dir(name)
        d.mkdir(parents=True, exist_ok=True)
        desc = {
            "profile": d.name,
            "created_at": time.time(),
            "last_seen": time.time(),
            "meta": meta or {},
        }
        (d / "session.json").write_text(json.dumps(desc, indent=2))
        return desc

    def save_state(self, name, state):
        """Persist arbitrary session state (tabs, scroll, form data)."""
        d = self._profile_dir(name)
        d.mkdir(parents=True, exist_ok=True)
        state = dict(state, saved_at=time.time())
        (d / "state.json").write_text(json.dumps(state, indent=2))
        return state

    def load_state(self, name):
        p = self._profile_dir(name) / "state.json"
        if not p.exists():
            return {}
        return json.loads(p.read_text())

    def touch(self, name):
        p = self._profile_dir(name) / "session.json"
        if p.exists():
            desc = json.loads(p.read_text())
            desc["last_seen"] = time.time()
            p.write_text(json.dumps(desc, indent=2))

    def list_profiles(self):
        out = []
        for d in sorted(self.data_dir.iterdir()):
            if d.is_dir():
                sj = d / "session.json"
                out.append(json.loads(sj.read_text()) if sj.exists()
                           else {"profile": d.name, "created_at": None})
        return out

    def delete(self, name, backup=True):
        """Delete a profile. With backup=True moves to <name>.bak-<ts> first."""
        d = self._profile_dir(name)
        if not d.exists():
            return False
        if backup:
            ts = int(time.time())
            d.rename(d.parent / f"{d.name}.bak-{ts}")
        else:
            shutil.rmtree(d)
        return True
