import json, subprocess, sys, tempfile
from pathlib import Path

def test_cli():
    with tempfile.TemporaryDirectory() as td:
        hp = Path(td) / "history.jsonl"
        hp.write_text("\n".join([
            json.dumps({"ts": 1792000000, "session": "s1", "action": "navigate",
                        "url": "https://example.com/a"}),
            json.dumps({"ts": 1792000100, "session": "s1", "action": "click",
                        "url": "https://example.com/a"}),
            json.dumps({"ts": 1792000200, "session": "s2", "action": "navigate",
                        "url": "https://other.org/"}),
        ]))
        r = subprocess.run(
            [sys.executable, "tools/query_history.py", "--history", str(hp),
             "--site", "example.com"],
            capture_output=True, text=True, cwd=".")
        assert r.returncode == 0, r.stderr
        assert "2 match(es)" in r.stdout, r.stdout
        print("query_history CLI OK")

if __name__ == "__main__":
    test_cli()
