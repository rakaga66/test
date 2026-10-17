#!/usr/bin/env python3
"""QAF carousel renderer, soft style (light warm paper, navy ink, rounded tiles).

Usage:  python3 scripts/render.py post.json OUT_DIR
Writes slide_01..NN.png and .jpg (1080x1350). Text auto-shrinks to fit (down to 80%);
prints OVERFLOW if a slide still does not fit, and MISSING-LOGO for logos that fell
back to a letter tile. Exit code 1 on any overflow.
See SPEC.md for the post.json format.
"""
import html, json, os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NM = ROOT / "node_modules"
FONT = ROOT / "fonts" / "doran-ar.ttf"  # Doran with Arabic kaf/yeh, built by arabize_font.py
FS = NM / "@fontsource"
W, H = 1080, 1350
BG, INK, MUTED, LINE, GREY, CARD = "#F0EFEB", "#0B0D2A", "#4A4D63", "#DBDAD6", "#7B7B80", "#FBFBF8"

ALIAS = {
    "chatgpt": "openai", "openai": "openai", "gpt": "openai", "sora": "openai",
    "gemini": "google-gemini", "gmail": "google-gmail", "calendar": "google-calendar",
    "google-calendar": "google-calendar", "drive": "google-drive", "google-drive": "google-drive",
    "claude-code": "claude", "copilot": "github-copilot", "mistral": "mistral-ai",
    "huggingface": "hugging-face", "xai": "x", "twitter": "x", "whatsapp": "whatsapp",
    "apple-calendar": "date", "calendar-date": "date", "reminders": "reminders", "apple": "si:apple", "sheets": "si:googlesheets",
    "google-sheets": "si:googlesheets", "docs": "si:googledocs", "google-docs": "si:googledocs",
    "slides": "si:googleslides", "google-slides": "si:googleslides", "edge": "microsoft-edge", "vscode": "visual-studio-code",
    "meet": "google-meet", "maps": "google-maps", "linkedin": "linkedin", "discord": "discord", "facebook": "facebook",
    "canva": "si:canva", "metricool": "text:M", "windsurf": "si:windsurf", "suno": "si:suno",
    "runway": "si:runway", "excel": "si:microsoftexcel", "word": "si:microsoftword",
    "powerpoint": "si:microsoftpowerpoint", "outlook": "si:microsoftoutlook", "teams": "si:microsoftteams",
    "amazon": "si:amazon", "higgsfield": "text:H",
    "hojas": "mono:HJS", "hojas-studio": "mono:HJS", "hjs": "mono:HJS", "qaf": "mono:QAF",
}

_sets, _si = {}, None


def iconset(name):
    if name not in _sets:
        p = NM / "@iconify-json" / name / "icons.json"
        _sets[name] = json.loads(p.read_text()) if p.exists() else {"icons": {}}
    return _sets[name]


def iconify(setname, name):
    S = iconset(setname)
    icons, aliases = S["icons"], S.get("aliases", {})
    seen = 0
    while name not in icons and name in aliases and seen < 5:
        name, seen = aliases[name]["parent"], seen + 1
    ic = icons.get(name)
    if not ic:
        return None
    w, h = ic.get("width", S.get("width", 16)), ic.get("height", S.get("height", 16))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{ic.get("left", 0)} {ic.get("top", 0)} {w} {h}">{ic["body"]}</svg>'


def simple_icon(slug):
    global _si
    if _si is None:
        _si = {}
        js = (NM / "simple-icons" / "index.js")
        if js.exists():
            for m in re.finditer(r'slug:"([^"]+)".*?path:"([^"]+)".*?hex:"([0-9A-Fa-f]{6})"', js.read_text()):
                _si[m.group(1)] = (m.group(2), m.group(3))
    v = _si.get(slug)
    if not v:
        return None
    path, hexc = v
    if hexc.upper() in ("000000", "FFFFFF", "191919", "181717"):
        hexc = INK[1:]
    return f'<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="#{hexc}" d="{path}"/></svg>'


MISSING = []


def tile(name, size="", label=None):
    """White rounded app tile with a full-colour logo. size: '' | 'sm' | 'xs'."""
    raw = (name or "").strip()
    key = ALIAS.get(raw.lower(), raw.lower())
    cls = f"tile {size}".strip()
    if key == "date":
        import datetime
        d = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
        return (f'<div class="{cls} datet"><div class="mo">{d.strftime("%b").upper()}</div>'
                f'<div class="dy">{d.day}</div></div>')
    if key == "reminders":
        rows = "".join(f'<circle cx="16" cy="{y}" r="7" fill="none" stroke="{c}" stroke-width="3.2"/><circle cx="16" cy="{y}" r="3.6" fill="{c}"/>'
                       f'<rect x="32" y="{y - 1.2}" width="48" height="2.4" rx="1.2" fill="#C9C9CE"/>'
                       for y, c in ((18, "#1C6FE0"), (40, "#E5483F"), (62, "#E89A1C")))
        return f'<div class="{cls}"><div class="g" style="width:66%;height:66%"><svg viewBox="0 0 84 80">{rows}</svg></div></div>'
    if key.startswith("mono:"):
        return f'<div class="{cls} mono"><span>{html.escape(key[5:])}</span></div>'
    if key.startswith("text:"):
        return f'<div class="{cls} txt"><span>{html.escape(key[5:])}</span></div>'
    svg = None
    if key.startswith("si:"):
        svg = simple_icon(key[3:])
    else:
        for cand in (key + "-icon", key):
            svg = iconify("logos", cand)
            if svg:
                vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
                if vb[2] / vb[3] > 1.8:  # a wide wordmark; a square brand glyph reads better in a tile
                    svg = simple_icon(key.replace("-", "")) or svg
                break
        if not svg:
            svg = iconify("skill-icons", key) or iconify("skill-icons", key + "-light")
            if svg:
                return f'<div class="{cls} full">{svg}</div>'
        if not svg:
            svg = simple_icon(key.replace("-", "").replace(" ", ""))
    if not svg:
        MISSING.append(raw)
        letter = html.escape((label or raw or "?")[:1].upper())
        return f'<div class="{cls} txt"><span>{letter}</span></div>'
    return f'<div class="{cls}"><div class="g">{svg}</div></div>'


def ui(name):
    return iconify("lucide", name) or iconify("lucide", "circle")


LATIN = re.compile(r"([A-Za-z@#][A-Za-z0-9@#_.+/&'’:\-]*(?:\s+[A-Za-z0-9@#][A-Za-z0-9@#_.+/&'’:\-]*)*)")


def t(s):
    """Escape, keep Latin runs isolated for clean bidi, \n -> <br>, [[x]] -> highlighted."""
    s = html.escape(str(s or ""))
    s = LATIN.sub(lambda m: f"<bdi{' class=nw' if len(m.group(1)) <= 30 else ''}>{m.group(1)}</bdi>", s)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1</span>', s)
    return s.replace("\n", "<br>")


def logos_html(names, size=""):
    return "".join(tile(n, size) for n in (names or []))


# ---------- mock UI cards ----------

def card(c):
    k = c.get("type", "menu")
    d = c.get("dir", "ltr")
    blur = "".join(f'<div class="sk" style="width:{w}%"></div>' for w in (c.get("skeleton") or []))
    hi = c.get("highlight")
    if k == "menu":
        rows = []
        for i, it in enumerate(c.get("items", [])):
            on = " on" if hi == i else ""
            rows.append(f'<div class="mi{on}"><span class="ic">{ui(it.get("icon", "circle"))}</span>'
                        f'<span class="ml">{t(it.get("label"))}</span><span class="ch">{ui("chevron-right" if d == "ltr" else "chevron-left")}</span></div>')
        body = "".join(rows)
    elif k == "toggle":
        rows = []
        for i, it in enumerate(c.get("items", [])):
            on = " on" if hi == i else ""
            sw = " sw-on" if it.get("on", True) else ""
            rows.append(f'<div class="mi{on}"><span class="ic">{ui(it.get("icon", "circle"))}</span>'
                        f'<span class="ml">{t(it.get("label"))}</span><span class="sw{sw}"><i></i></span></div>')
        body = "".join(rows)
    elif k == "connect":
        rows = []
        for i, it in enumerate(c.get("items", [])):
            on = " on" if hi == i else ""
            rows.append(f'<div class="mi{on}">{tile(it.get("logo", ""), "xs", it.get("label"))}'
                        f'<span class="ml">{t(it.get("label"))}</span><span class="pill">{t(it.get("action", "Connect"))}</span></div>')
        body = "".join(rows)
    elif k == "button":
        av_on = " on" if c.get("avatar_highlight") else ""
        btn_on = " on" if (hi is not None and not av_on) else ""
        icon = f'<span class="bi">{ui(c.get("icon", "plus"))}</span>' if c.get("icon") != "" else ""
        av = f'<span class="avatar{av_on}">{t(c.get("avatar"))}</span>' if c.get("avatar") else ""
        body = f'<div class="btnrow">{av}<span class="btn{btn_on}">{icon}{t(c.get("label"))}</span></div>'
    elif k == "input":
        typed = c.get("text")
        txt = f'<div class="in-t">{t(typed)}</div>' if typed else f'<div class="in-p">{t(c.get("placeholder", "How can I help you today?"))}</div>'
        model = f'<span class="model">{t(c.get("model", "Opus 5.5"))}</span>' if c.get("model", "Opus 5.5") else ""
        plus_on = " on" if hi == "plus" else ""
        body = (f'{txt}<div class="in-b"><span class="circ{plus_on}">{ui("plus")}</span>'
                f'<span class="sp"></span>{model}<span class="send">{ui("arrow-up")}</span></div>')
    elif k == "code":
        body = f'<pre class="code">{html.escape(c.get("text", ""))}</pre>'
    elif k == "chips":
        body = '<div class="chips">' + "".join(
            f'<span class="chip{" on" if hi == i else ""}">{t(x)}</span>' for i, x in enumerate(c.get("items", []))) + "</div>"
    elif k == "logos":
        body = '<div class="lg">' + "".join(
            f'<div class="lgi">{tile(it.get("logo", ""), "sm", it.get("label"))}<span>{t(it.get("label", ""))}</span></div>'
            for it in c.get("items", [])) + "</div>"
    elif k == "image":
        src = c.get("src", "")
        p = pathlib.Path(src)
        if p.exists():
            src = p.resolve().as_uri()
        body = f'<img class="shot" src="{html.escape(src)}">'
    else:
        body = t(c.get("text", ""))
    title = f'<div class="ct">{t(c["title"])}</div>' if c.get("title") else ""
    return f'<div class="card {k}" dir="{d}">{title}{blur}{body}</div>'


# ---------- slides ----------

def s_cover(s):
    return (f'<div class="main center">'
            f'<div class="logos">{logos_html(s.get("logos"))}</div>'
            f'<h1 class="cv-t fit">{t(s["title"])}</h1>'
            + (f'<p class="cv-s fit">{t(s["sub"])}</p>' if s.get("sub") else "") + "</div>")


def s_rows(s):
    head = f'<h2 class="head fit">{t(s["title"])}</h2>' if s.get("title") else ""
    rows = "".join(
        f'<div class="row"><div class="rl"><div class="rlab fit">{t(r["label"])}</div>'
        + (f'<div class="rsub fit">{t(r["sub"])}</div>' if r.get("sub") else "")
        + f'</div><div class="rlogos">{logos_html(r.get("logos"), "md" if len(r.get("logos") or []) > 2 else "")}</div></div>'
        for r in s.get("rows", []))
    return f'<div class="main">{head}<div class="rows">{rows}</div></div>'


def s_steps(s):
    out = []
    for i, st in enumerate(s.get("steps", [])):
        n = st.get("n", i + 1)
        out.append(f'<div class="step"><div class="sn">{n}</div>{card(st.get("card", {}))}'
                   f'<div class="cap fit">{t(st.get("caption", ""))}</div></div>')
    head = f'<h2 class="head c fit">{t(s["title"])}</h2>' if s.get("title") else ""
    lg = f'<div class="logos">{logos_html(s.get("logos"), "sm")}</div>' if s.get("logos") else ""
    return f'<div class="main center">{lg}{head}<div class="steps">{"".join(out)}</div></div>'


def s_text(s):
    lg = f'<div class="logos start">{logos_html(s.get("logos"), "sm")}</div>' if s.get("logos") else ""
    pts = ""
    if s.get("points"):
        pts = '<div class="pts">' + "".join(
            f'<div class="pt"><span class="pn">{i + 1}</span><span class="fit">{t(p)}</span></div>'
            for i, p in enumerate(s["points"])) + "</div>"
    body = f'<p class="tx-b fit">{t(s["body"])}</p>' if s.get("body") else ""
    note = f'<div class="card note"><div class="nt fit">{t(s["note"])}</div></div>' if s.get("note") else ""
    return f'<div class="main">{lg}<h2 class="tx-t fit">{t(s["title"])}</h2>{body}{pts}{note}</div>'


def s_prompt(s):
    c = {"type": "input", "text": s.get("prompt", ""), "model": s.get("model", ""), "dir": s.get("dir", "rtl")}
    cap = f'<div class="cap fit">{t(s["caption"])}</div>' if s.get("caption") else ""
    return (f'<div class="main center"><h2 class="head c fit">{t(s.get("title", ""))}</h2>'
            f'<div class="prompt">{card(c)}</div>{cap}</div>')


def s_compare(s):
    cols = []
    for c in s.get("cols", [])[:2]:
        pts = "".join(f'<li class="fit">{t(p)}</li>' for p in c.get("points", []))
        cols.append(f'<div class="col">{tile((c.get("logos") or [""])[0], "sm", c.get("name"))}'
                    f'<div class="cn">{t(c.get("name", ""))}</div><ul>{pts}</ul></div>')
    head = f'<h2 class="head c fit">{t(s["title"])}</h2>' if s.get("title") else ""
    foot = f'<div class="card note"><div class="nt fit">{t(s["verdict"])}</div></div>' if s.get("verdict") else ""
    return f'<div class="main">{head}<div class="cmp">{"".join(cols)}</div>{foot}</div>'


def s_news_cover(s):
    rows = "".join(
        f'<div class="row nrow"><div class="rl"><span class="nn">{i + 1:02d}</span><span class="nt2 fit">{t(it["title"])}</span></div>'
        f'<div class="rlogos">{logos_html((it.get("logos") or [])[:1], "xs")}</div></div>'
        for i, it in enumerate(s.get("items", [])))
    return (f'<div class="main"><div class="nc-d">{t(s.get("date", ""))}</div>'
            f'<h1 class="nc-t fit">{t(s.get("title", "أخبار الذكاء الاصطناعي"))}</h1>'
            f'<div class="rows tight">{rows}</div></div>')


def s_news(s):
    src = f'<div class="src">المصدر: {t(s["source"])}</div>' if s.get("source") else ""
    why = f'<div class="card note"><div class="wl">ليش يهمك؟</div><div class="nt fit">{t(s["why"])}</div></div>' if s.get("why") else ""
    return (f'<div class="main">'
            f'<div class="nh"><div class="nh-r"><div class="nh-n">{s.get("n", 1):02d}</div>'
            f'<div class="nh-c">{t(s.get("company", ""))}</div></div>'
            f'<div class="rlogos">{logos_html(s.get("logos"), "sm")}</div></div>'
            f'<h2 class="nw-t fit">{t(s["title"])}</h2><p class="nw-b fit">{t(s.get("body", ""))}</p>{why}{src}</div>')


def s_end(s):
    cta = ""
    if s.get("cta"):
        cta = f'<div class="card note cta"><div class="ctat fit">{t(s["cta"])}</div>' + (
            f'<div class="nt fit">{t(s["cta_sub"])}</div>' if s.get("cta_sub") else "") + "</div>"
    return (f'<div class="main center"><div class="logos">{logos_html(s.get("logos"), "sm")}</div>'
            f'<h1 class="cv-t fit">{t(s.get("title", ""))}</h1>'
            + (f'<p class="cv-s fit">{t(s["sub"])}</p>' if s.get("sub") else "") + f"{cta}</div>")


KINDS = {"cover": s_cover, "rows": s_rows, "steps": s_steps, "text": s_text, "prompt": s_prompt,
         "compare": s_compare, "news_cover": s_news_cover, "news": s_news, "end": s_end}


def css():
    serif = FS / "source-serif-4/files/source-serif-4-latin-400-normal.woff2"
    serif_b = FS / "source-serif-4/files/source-serif-4-latin-700-normal.woff2"
    mono = FS / "ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2"
    inter = FS / "inter/files/inter-latin-500-normal.woff2"
    S = lambda px: f"calc({px}px * var(--s))"
    # Doran is a Persian-numeral font: keep every digit out of it (they would show as ۴۵۶).
    no_digits = "U+0000-002F,U+003A-065F,U+066A-06EF,U+06FA-10FFFF"
    return f"""
@font-face{{font-family:Doran;src:url('{FONT.as_uri()}');unicode-range:{no_digits}}}
@font-face{{font-family:QNum;src:url('{serif_b.as_uri()}');unicode-range:U+0030-0039,U+002E,U+0025,U+002B,U+002C}}
@font-face{{font-family:QSerif;src:url('{serif.as_uri()}')}}
@font-face{{font-family:QMono;src:url('{mono.as_uri()}')}}
@font-face{{font-family:QUI;src:url('{inter.as_uri()}')}}
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--s:1}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{BG};color:{INK}}}
body{{direction:rtl;font-family:Doran,QNum,sans-serif;-webkit-font-smoothing:antialiased;font-feature-settings:"kern"}}
.card .ml,.card .pill,.btn,.in-p,.chip,.lgi span{{font-family:QUI,Doran,QNum,sans-serif}}
.datet{{flex-direction:column;justify-content:flex-start;overflow:hidden}}
.datet .mo{{width:100%;background:#E8483F;color:#fff;font:600 30px QUI;text-align:center;padding:8px 0 6px;letter-spacing:1px}}
.datet .dy{{font:400 76px/1.15 QUI;color:#1d1d1f;margin-top:6px}}
.tile.sm.datet .mo{{font-size:22px}} .tile.sm.datet .dy{{font-size:56px}}
.tile.xs.datet .mo{{font-size:15px;padding:4px 0 3px}} .tile.xs.datet .dy{{font-size:36px}}
.remt{{flex-direction:column;gap:12%;align-items:stretch;padding:0 17%}}
.remt div{{display:flex;align-items:center;gap:12%}} .remt i{{width:17%;aspect-ratio:1;border-radius:50%;border:3px solid currentColor;flex:none}}
.remt b{{flex:1;height:2px;background:#cfcfd4}}
bdi{{unicode-bidi:isolate}} bdi.nw{{white-space:nowrap}}
.slide{{width:{W}px;height:{H}px;padding:96px 132px 0;display:flex;flex-direction:column;position:relative}}
.main{{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:120px}}
.center{{align-items:center;text-align:center}}
.handle{{position:absolute;bottom:58px;left:0;right:0;text-align:center;font:400 27px QSerif;color:{GREY};direction:ltr}}
.hl{{background:linear-gradient(transparent 62%, #E3DED2 62%);padding:0 4px}}
/* tiles */
.tile{{width:156px;height:156px;border-radius:35px;background:#fff;display:flex;align-items:center;justify-content:center;
  box-shadow:0 10px 22px rgba(20,22,40,.09),0 1px 3px rgba(20,22,40,.07);flex:none}}
.tile .g{{width:58%;height:58%;display:flex;align-items:center;justify-content:center}}
.tile .g svg{{max-width:100%;max-height:100%;width:100%;height:100%}}
.tile.full{{overflow:hidden;background:none}} .tile.full svg{{width:100%;height:100%}}
.tile.txt span,.tile.mono span{{font:700 54px Doran;color:{INK}}}
.tile.mono{{background:{INK}}} .tile.mono span{{color:#fff;font:700 44px QMono;letter-spacing:2px}}
.tile.md{{width:132px;height:132px;border-radius:30px}}
.tile.sm{{width:118px;height:118px;border-radius:27px}} .tile.sm.txt span{{font-size:42px}} .tile.sm.mono span{{font-size:32px}}
.tile.xs{{width:76px;height:76px;border-radius:18px;box-shadow:0 5px 12px rgba(20,22,40,.08),0 1px 2px rgba(20,22,40,.07)}}
.tile.xs.txt span{{font-size:30px}} .tile.xs.mono span{{font-size:20px;letter-spacing:1px}}
.logos{{display:flex;gap:30px;justify-content:center;flex-wrap:wrap;margin-bottom:56px}}
.logos.start{{justify-content:flex-start;margin-bottom:44px;gap:22px}}
/* cover / end */
.cv-t{{font-size:{S(92)};line-height:1.32;font-weight:800}}
.cv-s{{font-size:{S(42)};line-height:1.6;color:{MUTED};margin-top:30px;max-width:780px}}
.head{{font-size:{S(64)};line-height:1.35;margin-bottom:50px}} .head.c{{text-align:center}}
/* rows */
.rows .row{{display:flex;align-items:center;justify-content:space-between;gap:40px;padding:58px 0;border-bottom:2px solid {LINE}}}
.rows .row:last-child{{border-bottom:none}}
.rows.tight .row{{padding:30px 0}}
.rl{{flex:1;min-width:0}}
.rlab{{font-size:{S(76)};line-height:1.25}}
.rsub{{font-size:{S(34)};line-height:1.5;color:{MUTED};margin-top:12px}}
.rlogos{{display:flex;gap:24px;flex:none;direction:ltr}}
/* steps */
.steps{{display:flex;flex-direction:column;gap:64px;align-items:center;width:100%}}
.step{{display:flex;flex-direction:column;align-items:center;width:100%}}
.sn{{font:400 34px QSerif;color:{MUTED};margin-bottom:22px}}
.cap{{font-size:{S(46)};line-height:1.45;margin-top:34px;max-width:820px}}
/* cards */
.card{{background:{CARD};border-radius:32px;box-shadow:0 12px 30px rgba(20,22,40,.08),0 1px 3px rgba(20,22,40,.06);
  width:640px;padding:30px 34px;text-align:start;font-family:Doran}}
.card[dir=ltr]{{direction:ltr}}
.card .ct{{font-size:28px;color:{GREY};margin-bottom:16px}}
.card .sk{{height:22px;border-radius:11px;background:#D9D8D3;filter:blur(5px);margin:14px 0 18px;opacity:.9}}
.mi{{display:flex;align-items:center;gap:24px;padding:20px 22px;border-bottom:2px solid #ECEBE6;border-radius:16px;font-size:31px;color:#25283d}}
.mi:last-child{{border-bottom:none}}
.mi .ic svg,.mi .ch svg{{width:34px;height:34px;color:#55586b;display:block}}
.mi .ch{{margin-inline-start:auto}} .mi .ch svg{{width:28px;height:28px;color:#8a8c99}}
.mi .ml{{flex:1}}
.mi.on{{outline:3.5px solid {INK};outline-offset:-2px;border-bottom-color:transparent}}
.sw{{width:74px;height:42px;border-radius:21px;background:#cfcfd4;position:relative;flex:none}}
.sw i{{position:absolute;top:5px;left:5px;width:32px;height:32px;border-radius:50%;background:#fff}}
.sw.sw-on{{background:{INK}}} .sw.sw-on i{{left:37px}}
.pill{{font-size:25px;padding:10px 22px;border-radius:999px;border:2px solid #cfcfd4;color:#25283d;flex:none}}
.mi.on .pill{{background:{INK};color:#fff;border-color:{INK}}}
.btnrow{{display:flex;align-items:center;gap:26px;justify-content:center;padding:6px 0}}
.btn{{display:inline-flex;align-items:center;gap:14px;background:#2A2A2E;color:#fff;font-size:30px;padding:18px 34px;border-radius:999px}}
.btn .bi svg{{width:30px;height:30px;display:block}}
.btn.on{{outline:3.5px solid {INK};outline-offset:6px}}
.avatar{{width:96px;height:96px;border-radius:50%;background:#fff;border:2px solid #d5d4cf;display:flex;align-items:center;justify-content:center;font:700 30px QMono;color:#25283d}}
.avatar.on{{outline:3.5px solid {INK};outline-offset:6px}}
.in-p{{font-size:30px;color:#9a9ca8;padding:8px 6px 30px}}
.in-t{{font-size:{S(36)};line-height:1.65;color:#1d2033;padding:6px 6px 30px}}
.in-b{{display:flex;align-items:center;gap:16px;direction:ltr}}
.in-b .sp{{flex:1}}
.circ,.send{{width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid #d9d8d3}}
.circ svg,.send svg{{width:30px;height:30px}}
.circ.on{{outline:3.5px solid {INK};outline-offset:4px}}
.send{{background:#C96442;border-color:#C96442;color:#fff}}
.model{{font:500 24px QMono;color:#6b6e7e}}
.code{{font:500 30px/1.6 QMono;color:#1d2033;white-space:pre-wrap;direction:ltr;text-align:left}}
.chips{{display:flex;flex-wrap:wrap;gap:16px}}
.chip{{font-size:29px;padding:14px 26px;border-radius:999px;background:#fff;border:2px solid #e2e1dc}}
.chip.on{{border-color:{INK};outline:2px solid {INK}}}
.lg{{display:flex;gap:30px;justify-content:center;flex-wrap:wrap}}
.lgi{{display:flex;flex-direction:column;align-items:center;gap:14px;font-size:26px;color:#3a3d52}}
.shot{{width:100%;border-radius:20px;display:block}}
.card.image{{padding:14px}}
.prompt .card{{width:820px;padding:40px 44px 30px}} .prompt .in-t{{font-size:{S(46)};line-height:1.7}}
/* text */
.tx-t{{font-size:{S(70)};line-height:1.35}}
.tx-b{{font-size:{S(40)};line-height:1.75;color:{MUTED};margin-top:30px}}
.pts{{margin-top:40px;display:flex;flex-direction:column}}
.pt{{display:flex;gap:28px;align-items:baseline;padding:26px 0;border-bottom:2px solid {LINE};font-size:{S(40)};line-height:1.55}}
.pt:last-child{{border-bottom:none}}
.pn{{font:400 34px QSerif;color:{GREY};min-width:30px}}
.card.note{{width:100%;margin-top:46px;padding:36px 42px}}
.note .nt{{font-size:{S(37)};line-height:1.7;color:#25283d}}
.note .wl{{font-size:{S(34)};color:{GREY};margin-bottom:10px}}
/* compare */
.cmp{{display:flex;gap:34px}}
.col{{flex:1;background:{CARD};border-radius:32px;padding:40px 34px;box-shadow:0 12px 30px rgba(20,22,40,.08),0 1px 3px rgba(20,22,40,.06);display:flex;flex-direction:column;align-items:center}}
.cn{{font-size:{S(46)};margin:24px 0 18px}}
.col ul{{list-style:none;width:100%}}
.col li{{font-size:{S(33)};line-height:1.55;padding:18px 0;border-bottom:2px solid #ECEBE6;color:#25283d}}
.col li:last-child{{border-bottom:none}}
/* news */
.nc-d{{font:400 34px QSerif;color:{GREY};direction:rtl}}
.nc-t{{font-size:{S(88)};line-height:1.3;margin:18px 0 34px}}
.nrow .rl{{display:flex;gap:26px;align-items:baseline}}
.nn{{font:400 32px QSerif;color:{GREY};flex:none}}
.nt2{{font-size:{S(40)};line-height:1.45}}
.nh{{display:flex;justify-content:space-between;align-items:center;padding-bottom:40px;border-bottom:2px solid {LINE};margin-bottom:44px}}
.nh-n{{font:400 40px QSerif;color:{GREY}}}
.nh-c{{font-size:44px;margin-top:6px}}
.nw-t{{font-size:{S(68)};line-height:1.38}}
.nw-b{{font-size:{S(39)};line-height:1.75;color:{MUTED};margin-top:28px}}
.src{{margin-top:36px;font-size:28px;color:{GREY}}}
.cta .ctat{{font-size:{S(44)};line-height:1.45;margin-bottom:10px}}
.cta{{text-align:center;max-width:820px}}
"""


FIT_JS = """
async () => {
  await Promise.allSettled([...document.fonts].map(f => f.load()));
  await document.fonts.ready;
  const sl = document.querySelector('.slide');
  const fits = () => sl.scrollHeight <= sl.clientHeight + 1 &&
    [...document.querySelectorAll('.fit')].every(e => e.scrollWidth <= e.clientWidth + 2);
  let s = 1;
  while (!fits() && s > 0.8) { s = +(s - 0.02).toFixed(2); document.documentElement.style.setProperty('--s', s); }
  const font = [...document.fonts].some(f => f.family.replace(/"/g, '') === 'Doran' && f.status === 'loaded');
  return {s, ok: fits(), h: sl.scrollHeight, font};
}
"""


def page(body, handle):
    return (f"<!doctype html><html lang='ar' dir='rtl'><head><meta charset='utf-8'><style>{css()}</style></head>"
            f"<body><div class='slide'>{body}<div class='handle'>{html.escape(handle)}</div></div></body></html>")


def main(data_path, out_dir):
    from playwright.sync_api import sync_playwright
    if not FONT.exists():
        sys.exit(f"ERROR: {FONT} missing, run scripts/setup.sh first")
    D = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    handle = D.get("handle", "@qaf_of")
    out = pathlib.Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("slide_*.*"):
        old.unlink()
    pages = []
    for s in D["slides"]:
        fn = KINDS.get(s.get("type"))
        if not fn:
            sys.exit(f"unknown slide type: {s.get('type')}")
        pages.append(page(fn(s), handle))
    bad = 0
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": W, "height": H})
        for k, doc in enumerate(pages, 1):
            f = out / f"slide_{k:02d}.html"
            f.write_text(doc, encoding="utf-8")
            pg.goto(f.as_uri())
            r = pg.evaluate(FIT_JS)
            pg.wait_for_timeout(150)
            if not r["font"]:
                sys.exit(f"ERROR slide {k}: the Doran font did not load, slides would use a fallback font")
            if not r["ok"]:
                bad += 1
                print(f"OVERFLOW slide {k}: content {r['h']}px even at 80% text, shorten it")
            elif r["s"] < 1:
                print(f"slide {k}: text scaled to {int(r['s'] * 100)}%")
            pg.screenshot(path=str(out / f"slide_{k:02d}.png"))
            pg.screenshot(path=str(out / f"slide_{k:02d}.jpg"), type="jpeg", quality=88)
            f.unlink()
        br.close()
    for m in sorted(set(MISSING)):
        print(f"MISSING-LOGO {m}: used a letter tile (try another name, see SPEC.md)")
    print(f"rendered {len(pages)} slides to {out}" + (f" ({bad} overflow)" if bad else ""))
    return bad


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(1 if main(sys.argv[1], sys.argv[2]) else 0)
