#!/usr/bin/env python3
"""Query the muse-browser history log. Pure stdlib — no downloads.

Usage:
  query_history.py [--history FILE] [--site example.com] [--since 2026-10-01]
                   [--until 2026-10-16] [--action click] [-q text] [--limit 20]
                   [--replay SESSION_ID]

Answers "what did I do on that site last Tuesday?"
"""
import argparse, json, sys
from datetime import datetime
from pathlib import Path

def parse_ts(s):
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).timestamp()
        except ValueError:
            continue
    raise ValueError(f"bad timestamp: {s}")

def load_history(path):
    entries = []
    p = Path(path)
    if not p.exists():
        return entries
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--history", default="history/history.jsonl")
    ap.add_argument("--site")
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--action")
    ap.add_argument("-q", "--query")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--replay")
    a = ap.parse_args()

    entries = load_history(a.history)
    if a.site:
        entries = [e for e in entries if a.site in str(e.get("url", ""))]
    if a.since:
        ts = parse_ts(a.since)
        entries = [e for e in entries if e.get("ts", 0) >= ts]
    if a.until:
        ts = parse_ts(a.until)
        entries = [e for e in entries if e.get("ts", 0) <= ts]
    if a.action:
        entries = [e for e in entries if e.get("action") == a.action]
    if a.replay:
        entries = [e for e in entries if e.get("session") == a.replay]
        entries.sort(key=lambda e: e.get("ts", 0))
    if a.query:
        q = a.query.lower()
        entries = [e for e in entries if q in json.dumps(e).lower()]

    for e in entries[-a.limit:]:
        ts = datetime.fromtimestamp(e.get("ts", 0)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{ts} [{e.get('session','?')}] {e.get('action','?')} {e.get('url','')}")
    print(f"-- {len(entries)} match(es), showing last {min(a.limit, len(entries))} --")

if __name__ == "__main__":
    main()
