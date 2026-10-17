# post.json: صيغة الشرائح

`python3 scripts/render.py post.json OUT_DIR` يرسم كل شريحة 1080x1350 (png و jpg).
التصميم ثابت: خلفية ورقية فاتحة، حبر كحلي، خط Doran (نسخة الكاف والياء العربية)، مربعات شعارات بيضاء بحواف ناعمة، والحساب تحت بالنص.
النص يصغر لحاله لين 80% لو ما وسعته الشريحة. لو طلع `OVERFLOW` اختصر. لو طلع `MISSING-LOGO` غيّر اسم الشعار.

```json
{"handle": "@qaf_of", "slides": [ ...شرائح... ]}
```

## أنواع الشرائح

| type | الحقول | متى |
|---|---|---|
| `cover` | `title` (سطرين بالكثير، استخدم `\n`)، `sub`، `logos` | أول شريحة في الحيلة |
| `rows` | `title` اختياري، `rows: [{label, sub?, logos}]` (2 إلى 4) | قائمة أشياء مع شعاراتها، نفس شكل المرجع |
| `steps` | `title` اختياري، `steps: [{card, caption}]` (خطوتين بالكثير) | خطوات داخل تطبيق |
| `text` | `title`، `body`، `points` (3 بالكثير)، `note`، `logos` | شرح فكرة |
| `prompt` | `title`، `prompt`، `caption`، `model` اختياري | برومت جاهز للنسخ |
| `compare` | `title`، `cols: [{logos:[x], name, points:[3]}]` (عمودين)، `verdict` | مقارنة أداتين |
| `news_cover` | `date`، `title`، `items: [{title, logos:[x]}]` (5) | غلاف الأخبار |
| `news` | `n`، `company`، `logos`، `title`، `body`، `why`، `source` | خبر واحد |
| `end` | `title`، `sub`، `cta`، `cta_sub`، `logos` | آخر شريحة |

حدود النص التقريبية: عنوان الغلاف 30 حرف للسطر. `caption` تحت الخطوة 40 حرف. `title` للخبر 60. `body` 150. `why` 110. نقطة في `points` 55.
`[[كلمة]]` تحط تحتها تظليل خفيف (مرة وحدة بالشريحة بالكثير). الأرقام اكتبها إنجليزية (5 مو ٥).
مط الحروف بالتطويل (مثل `الإيمـــيل`) مسموح في `label` حق `rows` بس، وبخفة.

## البطاقات (card) داخل `steps`
كل بطاقة تشبه جزء من واجهة التطبيق. اكتب أسماء الأزرار والقوائم **حرفيًا مثل التطبيق** (بالإنجليزي لو واجهته إنجليزي). `highlight` يحدد العنصر اللي عليه إطار.

| type | الحقول |
|---|---|
| `menu` | `items: [{icon, label}]`، `highlight: رقم` |
| `toggle` | `items: [{icon, label, on}]`، `highlight` |
| `connect` | `items: [{logo, label, action}]`، `highlight` |
| `button` | `label`، `icon`، `avatar` (حرفين)، `avatar_highlight: true`، `skeleton: [70,52]` أسطر ضبابية فوقه |
| `input` | `text` أو `placeholder`، `model`، `highlight: "plus"` |
| `code` | `text` (أمر أو كود قصير) |
| `chips` | `items: [نصوص]`، `highlight` |
| `logos` | `items: [{logo, label}]` |
| `image` | `src` مسار صورة حقيقية (لقطة شاشة) |

`dir`: `"ltr"` (الافتراضي، لواجهة إنجليزية) أو `"rtl"`.
أيقونات `icon` من مكتبة lucide: sliders-horizontal, code-xml, layout-grid, shield-check, audio-lines, plug, settings, plus, search, message-square, folder, user, mic, paperclip, sparkles, calendar, mail, bell, book-open, brain, globe, image, file-text, zap, wrench, puzzle, terminal, link, layers, send, bot, palette, monitor, smartphone, clock, list-checks.

## أسماء الشعارات (`logos`)
تنكتب صغيرة. أمثلة جاهزة:
claude, anthropic, chatgpt (= openai), gemini, google, gmail, calendar (تقويم جوجل), apple-calendar (مربع تاريخ اليوم), reminders, drive, docs, sheets, notion, slack, github, figma, canva, n8n, zapier, cursor, perplexity, midjourney, meta, microsoft, nvidia, apple, deepseek, mistral, huggingface, grok, x, tiktok, instagram, whatsapp, youtube, telegram, vercel, supabase, lovable, replit, elevenlabs, qwen, excel, word, powerpoint, outlook, teams, amazon, aws, samsung, copilot.
خاصة: `hojas` (شعار HJS لهوجاس ستوديو)، `qaf` (شعار QAF)، `text:X` (مربع بحرف).
أي اسم ثاني: جرّب اسم الشركة بالإنجليزي صغير بشرطات (مثل `hugging-face`)، وبعدها `si:<slug>` من simple-icons. لو ما فيه شعار، `text:` بأول حرف.
