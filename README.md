# muse-browser

**An open-source persistent browser for AI agents — a Linux VM browser with memory. No more permanent incognito mode.**

Every AI agent today browses the web in permanent incognito mode: no saved logins, no persistent cookies, no memory between tasks. Every site that needs a login is a cold start. Every session begins from zero, like it never met you.

muse-browser fixes that. It's a Linux-native, open-source browser built for agents, not humans:

- **Persistent profiles** — logins, cookies, and sessions survive VM restarts. Log in once, stay logged in.
- **Remote-driven API** — no GUI. The "user" is an AI agent making API calls: navigate, click, type, screenshot, extract.
- **Visible, persistent history** — every browsing action is logged and queryable. You can always see what the agent did.
- **Permission-gated** — the browser only acts with explicit permission. It never creates accounts or takes unauthorized actions (MuseAi-Guard principles: propose → approve → execute).

## Quickstart

```bash
pip install -r requirements.txt
python -m playwright install chromium

# Start the API server
python -m server.api

# In another terminal — drive it
python examples/basic_session.py
```

See [docs/QUICKSTART.md](docs/QUICKSTART.md) for the full walkthrough and [docs/API.md](docs/API.md) for the API reference.

## Architecture

```
┌─────────────┐     HTTP/REST      ┌──────────────────┐
│  AI Agent   │ ◄──────────────► │   API Server     │
│ (any client)│                  │  (FastAPI)       │
└─────────────┘                  └────────┬─────────┘
                                          │
                                 ┌────────▼─────────┐
                                 │  Browser Engine  │
                                 │  (Playwright +   │
                                 │   Chromium)      │
                                 └────────┬─────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    │                     │                     │
              ┌─────▼─────┐        ┌──────▼──────┐       ┌──────▼──────┐
              │ Profiles  │        │  History    │       │ Permissions │
              │ (on disk) │        │  (JSONL)    │       │  (gate)     │
              └───────────┘        └─────────────┘       └─────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

## Project status

Early scaffold — see [PROGRESS.md](PROGRESS.md) for what's built and what's next. Built in the open, one hourly run at a time.

## License

MIT — see [LICENSE](LICENSE).
