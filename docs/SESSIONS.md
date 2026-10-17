# Sessions & Profiles

## Model

- A **profile** is a disk directory: `profiles/<name>/` holding cookies,
  localStorage, `session.json` (descriptor) and `state.json` (tabs, scroll,
  form state). Profiles survive VM restarts — this is the whole point.
- A **session** is a live attachment to a profile: one running browser
  context. Closing a session ends the context; the profile stays.

## Rules

- One profile per trust domain: `work`, `personal`, `research`. Never mix.
- `SessionStore` (`core/session.py`) is the only writer to profile dirs.
- `delete()` backs up (`<name>.bak-<ts>`) by default — profiles are never
  silently destroyed.
- Profile names are sanitized to `[A-Za-z0-9-_]`.

## Save / restore flow

1. `create(name)` — make or reattach to a profile.
2. Drive the browser via the engine; call `save_state(name, {...})` with
   tabs/scroll/form snapshots whenever meaningful progress happens.
3. On restart: `create(name)` again, then `load_state(name)` to resume.

## Permissions

`permissions.yaml` sets per-profile policy. Read-only actions
(`text`, `a11y`, `screenshot`, `history.query`) auto-approve; everything
state-changing goes through the proposal queue (`core/approval_flow.py`).
Account creation is hard-denied at proposal time and can never be allowlisted.
