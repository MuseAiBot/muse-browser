"""Configuration for muse-browser."""
import os
from pathlib import Path

BASE_DIR = Path(os.environ.get("MUSEBROWSER_HOME", Path(__file__).resolve().parent.parent))
PROFILES_DIR = BASE_DIR / "profiles"
HISTORY_DIR = BASE_DIR / "history"
API_TOKEN = os.environ.get("MUSEBROWSER_TOKEN", "dev-token-change-me")
API_HOST = os.environ.get("MUSEBROWSER_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("MUSEBROWSER_PORT", "8777"))
HEADLESS = os.environ.get("MUSEBROWSER_HEADLESS", "1") == "1"

for d in (PROFILES_DIR, HISTORY_DIR):
    d.mkdir(parents=True, exist_ok=True)
