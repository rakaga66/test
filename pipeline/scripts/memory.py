#!/usr/bin/env python3
"""Memory of the noon tips posts, so nothing is posted twice. File: pipeline/data/tips.json

  python3 scripts/memory.py seen [N]        last N tips (default 90), newest first
  python3 scripts/memory.py add ENTRY.json  add one entry (refuses a key or a feature already used)
  python3 scripts/memory.py posted KEY      mark an entry as scheduled on Instagram

ENTRY.json:
  {"key": "claude-connectors-gmail", "date": "YYYY-MM-DD", "pool": "claude",
   "feature": "connectors", "tools": ["claude", "gmail"], "title": "...", "sources": ["https://..."]}
pool is one of: claude, claude-code, chatgpt, gemini, connectors, skills, plugins, prompts,
workflow, compare, hojas-studio, other.
"""
import json, os, re, sys
from datetime import date

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "tips.json")
POOLS = {"claude", "claude-code", "chatgpt", "gemini", "connectors", "skills", "plugins", "prompts",
         "workflow", "compare", "hojas-studio", "other"}
KEY_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def load():
    return json.load(open(PATH, encoding="utf-8")) if os.path.exists(PATH) else []


def save(items):
    items.sort(key=lambda x: (x["date"], x["key"]), reverse=True)
    json.dump(items, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "seen"
    items = load()
    if cmd == "seen":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        if not items:
            print("(no tips yet)")
        for it in items[:n]:
            print(f"{it['date']} | {it['pool']} | {it['feature']} | {it['key']} | {it['title']} | "
                  f"{'posted' if it.get('posted') else 'not posted'}")
        hs = [it["date"] for it in items if it["pool"] == "hojas-studio"]
        print(f"last hojas-studio post: {hs[0] if hs else 'never'}")
    elif cmd == "add":
        it = json.load(open(sys.argv[2], encoding="utf-8"))
        for f in ("key", "date", "pool", "feature", "title"):
            if not it.get(f):
                sys.exit(f"ERROR missing {f}")
        if not KEY_RE.match(it["key"]):
            sys.exit("ERROR key must be lowercase-with-hyphens")
        if it["pool"] not in POOLS:
            sys.exit(f"ERROR pool must be one of {sorted(POOLS)}")
        date.fromisoformat(it["date"])
        if any(x["key"] == it["key"] for x in items):
            sys.exit(f"DUPLICATE key {it['key']}: pick another topic")
        same = [x for x in items if x["feature"] == it["feature"] and x["pool"] == it["pool"]]
        if same and (date.fromisoformat(it["date"]) - date.fromisoformat(same[0]["date"])).days < 30:
            sys.exit(f"DUPLICATE feature {it['feature']} was posted {same[0]['date']}: pick another topic")
        it.setdefault("posted", False)
        items.append(it)
        save(items)
        print(f"added {it['key']}")
    elif cmd == "posted":
        for it in items:
            if it["key"] == sys.argv[2]:
                it["posted"] = True
                save(items)
                print(f"marked {it['key']} posted")
                return
        sys.exit(f"ERROR no entry {sys.argv[2]}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
