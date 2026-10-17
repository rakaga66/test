#!/usr/bin/env bash
# Publish one carousel's JPGs to this public repo so Metricool can pull them, then check every URL.
# Usage: bash scripts/host.sh OUT_DIR SLOT      SLOT = YYYY-MM-DD-tips | YYYY-MM-DD-news
# Prints one "<http code> <url>" line per slide; the last line is "ALL 200" or "NOT READY".
set -e
R="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$1"; SLOT="$2"
[[ "$SLOT" =~ ^20[0-9]{2}-[0-9]{2}-[0-9]{2}-(tips|news)$ ]] || { echo "ERROR: bad slot $SLOT"; exit 1; }
ls "$OUT"/slide_*.jpg >/dev/null
cd "$R"
git pull -q --rebase origin main || true
rm -rf "$SLOT"; mkdir -p "$SLOT"; cp "$OUT"/slide_*.jpg "$SLOT/"
# keep only the last 7 days of images (pipeline/ and README.md are never touched)
OLD=$(TZ=Asia/Riyadh date -d "-7 days" +%F)
for d in 20??-??-??*; do
  [ -d "$d" ] && [[ "${d:0:10}" < "$OLD" ]] && git rm -rq "$d"
done
git add -A "$SLOT"
git commit -qm "Carousel $SLOT" && git push -q origin main
ok=1
for f in $(ls "$SLOT" | sort); do
  u="https://raw.githubusercontent.com/rakaga66/test/main/$SLOT/$f"
  c=000
  for t in 1 2 3 4; do
    c=$(curl -s -o /dev/null -w "%{http_code}" "$u") || true
    [ "$c" = 200 ] && break
    sleep 30
  done
  echo "$c $u"
  [ "$c" = 200 ] || ok=0
done
[ $ok = 1 ] && echo "ALL 200" || echo "NOT READY"
