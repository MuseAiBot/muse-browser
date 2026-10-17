import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from core.history import HistoryLog
from core.permissions import PermissionGate


def test_history_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        h = HistoryLog(Path(td) / "h.jsonl")
        h.record("p1", "s1", "navigate", {"url": "https://example.com"}, "ok")
        h.record("p1", "s1", "click", {"selector": "#x"}, "ok")
        h.record("p2", "s9", "navigate", {"url": "https://x.test"}, "ok")
        assert len(h.query()) == 3
        assert len(h.query(profile="p1")) == 2
        assert len(h.query(action="click")) == 1
        print("history OK")


def test_gate():
    g = PermissionGate()
    assert g.check("default", "navigate", {"url": "https://example.com"}).allowed
    assert g.check("default", "click", {"selector": "#a"}).allowed
    d = g.check("default", "navigate", {"url": "https://example.com/signup"})
    assert not d.allowed and "account creation" in d.reason
    g2 = PermissionGate({"default": "read", "profiles": {}})
    assert not g2.check("default", "click", {"selector": "#a"}).allowed
    print("gate OK")


if __name__ == "__main__":
    test_history_roundtrip()
    test_gate()
    print("all tests passed")
