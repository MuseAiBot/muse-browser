# Quickstart

## 1. Install

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

Needs Python 3.10+.

## 2. Configure

```bash
export MUSEBROWSER_TOKEN="pick-a-strong-secret"   # required — API bearer token
export MUSEBROWSER_HOME="$HOME/.muse-browser"     # where profiles + history live
export MUSEBROWSER_PORT=8777
```

## 3. Start the server

```bash
python -m server.api
```

## 4. Drive it

```bash
python examples/basic_session.py
```

Or with curl:

```bash
T=http://127.0.0.1:8777
H="Authorization: Bearer $MUSEBROWSER_TOKEN"

SID=$(curl -s -X POST $T/v1/sessions -H "$H" -H 'Content-Type: application/json' \
  -d '{"profile":"default"}' | python3 -c 'import json,sys; print(json.load(sys.stdin)["session_id"])')

curl -s -X POST $T/v1/sessions/$SID/navigate -H "$H" -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'

curl -s "$T/v1/sessions/$SID/text" -H "$H" | head -c 500

curl -s "$T/v1/history?profile=default&limit=5" -H "$H"
```

## Profiles survive restarts

Kill the server, reboot the machine — `profiles/default/` is still on disk.
Start the server again, open a session on the same profile, and you're logged in
wherever you were. That's the whole point.

## Permissions

Default policy allows `read` + `interact`, denies `state_changing` unless granted.
Account creation URLs are hard-denied always. See `core/permissions.py` and
`ARCHITECTURE.md`.
