#!/usr/bin/env bash
# One-time setup per session: fetch the licensed font from the private repo, build the
# Arabic-form copy, install icons, check Chromium.
# Needs a clone of rakaga66/qaf-private at $QAF_PRIVATE (default $HOME/qaf-private).
set -e
P="$(cd "$(dirname "$0")/.." && pwd)"
PRIV="${QAF_PRIVATE:-$HOME/qaf-private}"
cd "$P"
mkdir -p fonts
if [ ! -f fonts/doran-fanum-extrabold.ttf ]; then
  [ -f "$PRIV/fonts/doran-fanum-extrabold.ttf" ] || { echo "ERROR: font missing, clone rakaga66/qaf-private to $PRIV first"; exit 1; }
  cp "$PRIV/fonts/doran-fanum-extrabold.ttf" fonts/
fi
python3 -c "import fontTools" 2>/dev/null || pip install --break-system-packages -q fonttools
[ -f fonts/doran-ar.ttf ] || python3 scripts/arabize_font.py
[ -d node_modules/@iconify-json/logos ] || npm ci --silent --no-audit --no-fund
python3 -c "import playwright" 2>/dev/null || pip install --break-system-packages -q playwright
# Chromium is preinstalled (PLAYWRIGHT_BROWSERS_PATH); do not run "playwright install".
python3 -c "from playwright.sync_api import sync_playwright as s; p=s().start(); p.chromium.launch().close(); p.stop()"
echo "setup ok: $P"
