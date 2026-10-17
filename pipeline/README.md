# QAF carousel pipeline

Two daily Instagram carousels for @qaf_of, made by scheduled Claude runs (Opus 5.5):

| run starts | posts | runbook | images folder |
|---|---|---|---|
| ~12:50 | 14:00 | RUNBOOK_TIPS.md (one practical AI tip) | `YYYY-MM-DD-tips/` |
| ~20:50 | 22:00 | RUNBOOK_NEWS.md (5 verified AI news) | `YYYY-MM-DD-news/` |

- `scripts/render.py` draws the slides from `post.json` (format in SPEC.md).
- The licensed Doran font lives only in the private repo `rakaga66/qaf-private` (`fonts/doran-fanum-extrabold.ttf`); `setup.sh` copies it from `$HOME/qaf-private` and builds an Arabic kaf/yeh copy. Never commit a `.ttf` here.
- Memory so nothing repeats: tips in `data/tips.json`, news in `rakaga66/hojas-studio/site/data/news.json`.
- Images are pushed to date folders at the repo root and kept 7 days; Metricool pulls them from raw.githubusercontent.com.
