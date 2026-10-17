# PROGRESS.md — build log (hourly runs)

## Run 1 — 2026-10-16 ~20:05 EDT — scaffold

**Built:**
- `README.md` — project pitch, quickstart, architecture diagram
- `ARCHITECTURE.md` — full system design: engine, profiles, REST API, history log, permission gate
- `LICENSE` (MIT), `requirements.txt`
- `core/` — `engine.py` (Playwright persistent-context engine), `history.py` (JSONL audit log), `permissions.py` (action-class gate + hard no-account-creation rule), `config.py`
- `server/api.py` — FastAPI REST API: sessions, navigate/click/type/text/screenshot/evaluate, history query, profiles list, bearer-token auth
- `docs/QUICKSTART.md`, `docs/API.md`
- `examples/basic_session.py` — engine-level demo incl. permission-gate denial demo
- `tests/test_history.py` — history roundtrip + gate tests (passing)

**Not yet verified:** live Playwright run (Chromium download in progress during this run).

## Next (Run 2)

1. Verify Playwright/Chromium works: run `examples/basic_session.py` against example.com; confirm profile dir persists on disk and history.jsonl has entries.
2. Boot `server/api.py`, exercise endpoints with curl (session → navigate → text → history).
3. Add `permissions.yaml` support (per-profile policy file loaded by the gate).
4. Screenshot return path test via API.
5. Consider: session replay from history (stretch).

## Later

- WebSocket live action feed
- URL allowlists per profile
- Muse skill + connector packaging (skill requiring this connector)
- GitHub Pages docs site
