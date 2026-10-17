"""muse-browser core: persistent browser engine, history, permissions."""
from .engine import BrowserEngine
from .history import HistoryLog
from .permissions import PermissionGate, ActionClass

__all__ = ["BrowserEngine", "HistoryLog", "PermissionGate", "ActionClass"]
