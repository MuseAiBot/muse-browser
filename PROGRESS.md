# PROGRESS.md — build log

## Run 1 — 2026-10-16 ~20:05 EDT — scaffold

**Built:**
- `README.md` — project pitch, quickstart, architecture diagram
- `ARCHITECTURE.md` — full system design: engine, profiles, REST API, history log, permission gate
- `LICENSE` (MIT), `requirements.txt`
- `core/` — `engine.py` (Playwright persistent-context engine), `history.py` (JSONL audit log), `permissions.py` (action-class gate + hard no-account-creation rule), `config.py`
- `server/api.py` — FastAPI REST API: sessions, navigate/click/type/text/screenshot/evaluate, history query, profiles list, bearer-token auth
- `docs/QUICKSTART.md`, `docs/API.md`
- `examples/basic_session.py` — engine-level demo incl. permission-gate denial demo
- `tests/test_history.py` — history roundtrip + gate tests

## Run 2 — 2026-10-16 ~20:10–20:30 EDT — recovery rebuild (no downloads)

**What happened:** Run 2's first attempt built 5 chunks (connector doc, skill,
session persistence, approval flows, history CLI, docs) and pushed them — but
all commits and files vanished from the local clone afterwards and never
landed on origin (remote stayed at 3 commits). Cause unknown; possibly the
worker shutdown rolled back the workspace. Per Git-FED's stop-cleanly rule,
the work was rewritten from scratch in one pass, pure code, zero downloads.

**Rebuilt and verified:**
- `connector/` — `CONNECTOR.md`, `connector.yaml`, `README.md`, `helper.sh`
  (shell wrapper for the REST API)
- `muse-browser-skill/` — `SKILL.md` (agent workflow), `skill.json`
  (requires_connector: muse-browser), `README.md`
- `core/session.py` — `SessionStore`: create/reattach profiles, save/load
  state, list, backup-on-delete. `tests/test_session.py` passing.
- `core/approval_flow.py` — `ApprovalQueue`: propose → approve/reject →
  execute, agent can never self-approve, account creation hard-denied at
  proposal time. `tests/test_approval_flow.py` passing.
- `permissions.yaml` — per-profile policy (auto_approve vs require_approval)
- `tools/query_history.py` — CLI answering "what did I do on that site last
  Tuesday?" (`--site/--since/--until/--action/-q/--replay`). Tested.
- `docs/SESSIONS.md` — session/profile model and rules.

**Standing rule (Git-FED, 2026-10-16):** NO DOWNLOADS — no pip/npm install, no
curl/wget of packages, no cloning external repos, no venv creation. Pure
code: write, commit, push. Dependencies listed in requirements.txt only.

## Next

1. Wire `ApprovalQueue` + `permissions.yaml` into `server/api.py` endpoints
   (proposal queue REST surface).
2. Session replay endpoint (`GET /sessions/{id}/replay`).
3. URL allowlists per profile.
4. WebSocket live action feed (later).
5. GitHub Pages docs site (later).
