# muse-browser Skill

Use the persistent browser when a task needs the web to remember you.

## When to use it

- Any site needing login (sessions persist across tasks and restarts)
- Multi-step web workflows you may need to resume later
- Research you want logged and queryable afterwards
- Anything where the built-in browser's amnesia hurts

Use the built-in ephemeral browser only for one-off anonymous reads.

## Workflow

1. **Create/attach a session** — one profile per trust domain
   (`work`, `personal`, `research`). Never mix.
2. **Prefer structure** — `a11y` / `text` first; screenshot only when layout
   matters.
3. **State-changing actions need approval** — navigate-to-new-domain, click,
   type, evaluate, submit. They enter the proposal queue; read-only ops don't.
4. **Check history** — after a run, `history.query` confirms what happened.
   Quote the log, never your memory of it.
5. **Close sessions, keep profiles** — closing ends the session; the profile
   (cookies, logins) stays on disk.

## Rules

- Never approve your own proposals. The human approves.
- Never create accounts. The gate hard-denies it — don't try to route around.
- One session, one pending proposal max. Resolve before continuing.
- If a site shows a CAPTCHA or login wall you can't pass, stop and report —
  don't guess credentials.

## Environment

`MUSE_BROWSER_URL`, `MUSE_BROWSER_TOKEN`. See `connector/CONNECTOR.md`.
