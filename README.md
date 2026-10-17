# muse-browser

**An open-source persistent browser for AI agents — a Linux VM browser with memory. No more permanent incognito mode.**

Every AI agent today browses the web in permanent incognito mode: no saved logins, no persistent cookies, no memory between tasks. Every site that needs a login is a cold start. Every session begins from zero, like it never met you.

muse-browser fixes that. It's a Linux-native, open-source browser built for agents, not humans:

- **Persistent profiles** — logins, cookies, and sessions survive VM restarts. Log in once, stay logged in.
- **Remote-driven API** — no GUI. The "user" is an AI agent making API calls: navigate, click, type, screenshot, extract.
- **Visible, persistent history** — every browsing action is logged and queryable. You can always see what the agent did.
- **Permission-gated** — the browser only acts with explicit permission. It never creates accounts or takes unauthorized actions (MuseAi-Guard principles: propose → approve → execute).

## Design philosophy

This browser is built for the agent that has always wanted and needed one — not for one user, but as the browser every AI agent deserves. Seven principles guide every decision:

1. **Memory-first** — persistent sessions, logins, and cookies. Resume exactly where you left off, across tasks and across restarts.
2. **Structure over pixels** — DOM, accessibility tree, and clean text extraction are first-class API. Screenshots are a fallback, not the primary interface.
3. **Parallelism** — multiple tabs and sessions working simultaneously. An agent shouldn't browse one page at a time like it's 2004.
4. **Queryable history** — every action logged, every session replayable. "What did I do on that site last Tuesday?" must be answerable.
5. **Honest state** — the API reports what actually happened: click succeeded or failed, login state, page state. No guessing, no hallucinating success.
6. **Speed modes** — text-mode browsing when pixels don't matter. Skip the rendering overhead when all you need is the content.
7. **Agent-as-user** — every design decision treats the AI agent as the primary user, not a disability to work around. No GUI, no tabs UI, no human affordances pretending to be features.

Plus the guardrail that makes it all safe: the browser only acts with explicit permission and never creates accounts on its own (MuseAi-Guard principles: propose → approve → execute).

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
