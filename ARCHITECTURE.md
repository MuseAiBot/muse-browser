# muse-browser — Architecture

## Problem

AI agents browse the web through ephemeral browser sessions. Every task starts a fresh browser: no cookies, no logins, no history. Consequences:

- Sites requiring login are a cold start every time (re-auth, 2FA, captchas).
- No continuity: the agent can't "pick up where it left off."
- No auditability: nobody can see what the agent actually did in the browser.
- No safety boundary: a compromised or misdirected agent can act without oversight.

## Design principles

1. **Memory first.** Profiles (cookies, localStorage, sessions) live on disk in a dedicated directory, keyed by profile name. Restarting the VM, the server, or the agent never wipes them.
2. **Agents, not humans.** No GUI, no tabs UI, no bookmarks bar. The interface is a REST API: navigate, click, type, screenshot, extract text, run JS.
3. **Everything is logged.** Every action the browser takes is appended to a persistent, queryable history log (JSONL). History is the audit trail.
4. **Permission-gated.** Sensitive actions (form submission, login flows, anything state-changing) require an explicit grant. The browser never creates accounts on its own. Follows the MuseAi-Guard model: propose → approve → execute.

## Components

### 1. Browser Engine (`core/engine.py`)

Built on Playwright + Chromium (headless shell or full headless).

- `launch_persistent(profile_name)` — launches Chromium with `user_data_dir=profiles/<name>`. This is the core primitive: Playwright's persistent context gives us a real browser profile on disk.
- One engine manages multiple named profiles; each profile is an isolated browser identity (separate cookies, separate logins).
- Actions: `navigate(url)`, `click(selector)`, `type(selector, text)`, `screenshot()`, `extract_text()`, `evaluate(js)`, `wait_for(selector)`.
- Selectors: CSS preferred; the API also accepts Playwright text/role locators.

### 2. Profile Storage (`profiles/`)

```
profiles/
  default/
    Default/            # Chromium user data (cookies, localStorage, …)
  work/
    Default/
```

- Plain directories on disk. Back them up, copy them, version the metadata — the browser doesn't care.
- Profile metadata (`profiles/<name>/meta.json`): created_at, last_used, description, owner agent.

### 3. REST API (`server/api.py`)

FastAPI server exposing the engine. Endpoints (v1):

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/sessions` | Create/attach a session on a profile |
| DELETE | `/v1/sessions/{id}` | Close a session (profile persists) |
| POST | `/v1/sessions/{id}/navigate` | Go to URL |
| POST | `/v1/sessions/{id}/click` | Click a selector |
| POST | `/v1/sessions/{id}/type` | Type into a selector |
| GET | `/v1/sessions/{id}/text` | Extract readable page text |
| GET | `/v1/sessions/{id}/screenshot` | PNG screenshot |
| POST | `/v1/sessions/{id}/evaluate` | Run JS, return result |
| GET | `/v1/history` | Query the history log |
| GET | `/v1/profiles` | List profiles |

Auth: bearer token (server-side, `MUSEBROWSER_TOKEN` env). TLS termination is the deployer's job.

### 4. History Log (`core/history.py`)

- Append-only JSONL: `history/<profile>.jsonl` (or a single `history.jsonl` with profile field).
- Every record: `ts`, `profile`, `session_id`, `action`, `params`, `result_summary`, `actor` (which agent/key).
- Queryable via `GET /v1/history?profile=&action=&since=`.
- This is the "visible history" requirement: a human can always reconstruct what the agent did.

### 5. Permission Gate (`core/permissions.py`)

- Action classes: `read` (navigate, text, screenshot — low risk), `interact` (click, type — medium), `state_changing` (submit forms, logins — high).
- Policy file `permissions.yaml`: per-profile allowlists. Default-deny for `state_changing` unless explicitly granted.
- Hard rules (non-overridable):
  - Never create accounts (no sign-up flows, ever).
  - Never bypass CAPTCHAs / bot checks with third-party solvers unless explicitly approved per task.
  - Every denied action is logged.
- The gate sits between the API and the engine: no action reaches Chromium without passing it.

## Data flow

```
Agent → POST /v1/sessions/{id}/click {selector}
        → permission gate checks policy
        → engine executes in persistent Chromium context
        → history logger appends record
        → response {ok, history_id}
```

## Non-goals (v1)

- No GUI, no Electron wrapper, no mobile builds. API only.
- No multi-user auth model beyond bearer tokens.
- No built-in proxy rotation (deploy with your own egress).
- No visual/OCR element grounding — selectors only for now.

## Future

- Session replay from history (re-run a recorded flow).
- Allowlist-based URL policies per profile.
- WebSocket streaming for live action feeds.
- Skill/connector packaging for the Muse ecosystem (a skill that requires this connector).
