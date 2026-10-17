# API reference (v1)

All endpoints except `/healthz` require `Authorization: Bearer <token>`.

## Sessions

**POST /v1/sessions** — create a session on a profile (launches persistent Chromium context if needed).
```json
{"profile": "default", "actor": "agent"}
```
→ `{"session_id": "a1b2c3…", "profile": "default"}`

**DELETE /v1/sessions/{id}** — close the session. The profile (cookies, logins) persists.

## Actions

**POST /v1/sessions/{id}/navigate** — `{"url": "https://…"}`
**POST /v1/sessions/{id}/click** — `{"selector": "css selector"}`
**POST /v1/sessions/{id}/type** — `{"selector": "…", "text": "…"}`
**GET /v1/sessions/{id}/text** — page body text (truncated server-side).
**GET /v1/sessions/{id}/screenshot** — PNG bytes.
**POST /v1/sessions/{id}/evaluate** — `{"js": "document.title"}` → result.

Denied-by-policy actions return `403` with the reason; the denial is also logged.

## History

**GET /v1/history?profile=&action=&since=&limit=**
Every action ever taken, append-only. `since` is a unix timestamp.

## Profiles

**GET /v1/profiles** — list profile names on disk.

## Health

**GET /healthz** — `{"ok": true}`.
