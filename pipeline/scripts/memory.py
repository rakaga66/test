#!/usr/bin/env python3
"""Memory of the noon tips posts, so nothing is posted twice. File: pipeline/data/tips.json

  python3 scripts/memory.py seen [N]        last N tips (default 90), newest first
  python3 scripts/memory.py add ENTRY.json  add one entry. Refuses: a used key, the same feature within 45 days,
                                            the same pool as either of the last 2 posts, hojas-studio twice in 7 days
  python3 scripts/memory.py posted KEY      mark an entry as scheduled on Instagram
  python3 scripts/memory.py drop KEY        remove an entry that never got scheduled

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


def norm(feature):
    """'Connectors', 'connector', 'MCP connectors ' -> comparable form."""
    words = re.sub(r"[^a-z0-9]+", " ", feature.lower()).split()
    return "-".join(w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words)


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
        today = date.fromisoformat(it["date"])
        same = [x for x in items if norm(x["feature"]) == norm(it["feature"])]
        if same and (today - date.fromisoformat(same[0]["date"])).days < 45:
            sys.exit(f"DUPLICATE feature {it['feature']} was posted {same[0]['date']}: pick another topic")
        last2 = [x["pool"] for x in items[:2]]
        if it["pool"] in last2 and it["pool"] != "other":
            sys.exit(f"SAME POOL {it['pool']} as one of the last 2 posts {last2}: pick another pool")
        hs = [x for x in items if x["pool"] == "hojas-studio"]
        if it["pool"] == "hojas-studio" and hs and (today - date.fromisoformat(hs[0]["date"])).days < 7:
            sys.exit(f"TOO SOON hojas-studio was posted {hs[0]['date']}: max once every 7 days")
        it.setdefault("posted", False)
        items.append(it)
        save(items)
        print(f"added {it['key']}")
    elif cmd == "drop":
        keep = [x for x in items if not (x["key"] == sys.argv[2] and not x.get("posted"))]
        if len(keep) == len(items):
            sys.exit(f"ERROR no unposted entry {sys.argv[2]}")
        save(keep)
        print(f"dropped {sys.argv[2]}")
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
