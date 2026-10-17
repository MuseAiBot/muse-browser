"""Propose → approve → execute flow for state-changing browser actions.

Pure stdlib. The human (or policy) resolves proposals; the agent never
approves its own. Account creation is denied at proposal time, always.
"""
import json, time, uuid
from pathlib import Path

ACCOUNT_CREATION_SIGNALS = (
    "signup", "sign-up", "register", "create-account", "create_account",
)

class ApprovalQueue:
    def __init__(self, data_dir="profiles"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._file = self.data_dir / "approvals.json"
        self._load()

    def _load(self):
        if self._file.exists():
            self._q = json.loads(self._file.read_text())
        else:
            self._q = {"pending": {}, "resolved": {}}

    def _save(self):
        self._file.write_text(json.dumps(self._q, indent=2))

    def _is_account_creation(self, action, detail):
        blob = f"{action} {json.dumps(detail)}".lower()
        return any(s in blob for s in ACCOUNT_CREATION_SIGNALS)

    def propose(self, session_id, action, detail=None):
        """Propose an action. Returns (proposal_id, status).
        status is 'denied' for account creation, else 'pending'."""
        detail = detail or {}
        if self._is_account_creation(action, detail):
            return None, "denied"
        pid = uuid.uuid4().hex[:12]
        self._q["pending"][pid] = {
            "id": pid, "session": session_id, "action": action,
            "detail": detail, "proposed_at": time.time(), "status": "pending",
        }
        self._save()
        return pid, "pending"

    def pending(self, session_id=None):
        items = list(self._q["pending"].values())
        if session_id:
            items = [i for i in items if i["session"] == session_id]
        return items

    def resolve(self, pid, approved, resolved_by):
        """Resolve a proposal. resolved_by must not be the proposing agent."""
        item = self._q["pending"].pop(pid, None)
        if not item:
            return None
        item["status"] = "approved" if approved else "rejected"
        item["resolved_at"] = time.time()
        item["resolved_by"] = resolved_by
        self._q["resolved"][pid] = item
        self._save()
        return item
