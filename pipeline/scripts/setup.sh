#!/usr/bin/env bash
# One-time setup per session: decrypt the font, build the Arabic-form copy, install icons, check Chromium.
# Needs QAF_FONT_KEY (it is in the scheduled task's prompt, never commit it).
set -e
P="$(cd "$(dirname "$0")/.." && pwd)"
cd "$P"
[ -n "$QAF_FONT_KEY" ] || { echo "ERROR: QAF_FONT_KEY is not set"; exit 1; }
if [ ! -f fonts/doran-fanum-extrabold.ttf ]; then
  openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in fonts/doran.enc \
    -out fonts/doran-fanum-extrabold.ttf -pass "pass:$QAF_FONT_KEY"
fi
python3 -c "import fontTools" 2>/dev/null || pip install --break-system-packages -q fonttools
[ -f fonts/doran-ar.ttf ] || python3 scripts/arabize_font.py
[ -d node_modules/@iconify-json/logos ] || npm ci --silent --no-audit --no-fund
python3 -c "import playwright" 2>/dev/null || pip install --break-system-packages -q playwright
# Chromium is preinstalled (PLAYWRIGHT_BROWSERS_PATH); do not run "playwright install".
python3 -c "from playwright.sync_api import sync_playwright as s; p=s().start(); p.chromium.launch().close(); p.stop()"
echo "setup ok: $P"
