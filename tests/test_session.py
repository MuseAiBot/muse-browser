import sys, tempfile
sys.path.insert(0, "core")
from pathlib import Path
from session import SessionStore

def test_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        s = SessionStore(td)
        d = s.create("work", meta={"owner": "agent"})
        assert d["profile"] == "work"
        s.save_state("work", {"tabs": ["https://example.com"], "scroll": 120})
        assert s.load_state("work")["scroll"] == 120
        assert any(p["profile"] == "work" for p in s.list_profiles())
        assert s.delete("work")
        assert not (Path(td) / "work").exists()
        print("session roundtrip OK")

if __name__ == "__main__":
    test_roundtrip()
