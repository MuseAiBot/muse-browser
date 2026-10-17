# muse-browser Connector

Drive a persistent, permission-gated browser for AI agents over HTTP.

## Connection

- `MUSE_BROWSER_URL` — base URL of the server (default `http://localhost:8765`)
- `MUSE_BROWSER_TOKEN` — bearer token (server-side `MUSE_BROWSER_TOKEN` env)

Every request carries `Authorization: Bearer <token>`.

## Operations

| Op | Method & path | Purpose |
|---|---|---|
| status | `GET /status` | health + version + active sessions |
| session.create | `POST /sessions {"profile": "name"}` | create or attach to a persistent session |
| session.list | `GET /sessions` | list sessions |
| session.close | `DELETE /sessions/{id}` | close (profile persists on disk) |
| navigate | `POST /sessions/{id}/navigate {"url"}` | go to URL |
| click | `POST /sessions/{id}/click {"selector"}` | click CSS selector |
| type | `POST /sessions/{id}/type {"selector","text"}` | type into field |
| text | `GET /sessions/{id}/text` | page as clean text |
| a11y | `GET /sessions/{id}/a11y` | accessibility tree (structure-first) |
| screenshot | `GET /sessions/{id}/screenshot` | PNG bytes (fallback only) |
| evaluate | `POST /sessions/{id}/evaluate {"js"}` | run JS, return result |
| history.query | `GET /history?q=&site=&since=&until=&action=&limit=` | query the persistent log |
| history.replay | `GET /sessions/{id}/replay?since=` | actions since timestamp |
| profiles.list | `GET /profiles` | disk profiles |

## Permission model

State-changing actions (navigate to a new registrable domain, click, type,
evaluate, form submit) enter the **proposal queue** unless the session's
`permissions.yaml` sets `auto_approve` for that action class. Read-only ops
(text, a11y, screenshot, history) never need approval.

`POST /approvals` lists pending proposals; `POST /approvals/{id}/approve`
or `/reject` resolves them. The browser never creates accounts, never submits
credentials it wasn't explicitly handed, never acts without approval.

## Errors

- `401` bad/missing token → check `MUSE_BROWSER_TOKEN`
- `403` action denied by permission gate → inspect proposal, adjust `permissions.yaml`
- `409` session already has a pending proposal → resolve it first
- `410` profile corrupted → restore from backup or start fresh (explicit)
