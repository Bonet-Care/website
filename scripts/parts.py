"""Shared pieces: languages, string lookup, head, header (with the language menu), footer, prices."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://bonet.care"
APP = "https://app.bonet.care"
MAIL = "hello@coglixlabs.com"
GA = "G-WMQD9MWHJN"
LASTMOD = "2026-11-13"

# order = order in the menu. name is written in the language itself.
LANGS = {
    "en": {"name": "English", "path": "/", "tag": "en", "html": "en"},
    "zh-hant": {"name": "繁體中文", "path": "/zh-hant/", "tag": "zh-Hant", "html": "zh-Hant"},
    "yue": {"name": "廣東話", "path": "/yue/", "tag": "yue-Hant-HK", "html": "yue-Hant-HK"},
    "zh-hans": {"name": "简体中文", "path": "/zh-hans/", "tag": "zh-Hans", "html": "zh-Hans"},
    "ja": {"name": "日本語", "path": "/ja/", "tag": "ja", "html": "ja"},
    "es": {"name": "Español", "path": "/es/", "tag": "es", "html": "es"},
    "de": {"name": "Deutsch", "path": "/de/", "tag": "de", "html": "de"},
    "fr": {"name": "Français", "path": "/fr/", "tag": "fr", "html": "fr"},
}
NUM_WORD = {6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}
NUM_YUE = {6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}
LANG_COUNT = len(LANGS)

# ---- strings: the template holds the English text and the Cantonese gloss; strings/<lang>.json maps English -> that language.
STR = {}
MISSING = {}
REGISTRY = {}
for code in LANGS:
    f = ROOT / "strings" / f"{code}.json"
    STR[code] = json.loads(f.read_text()) if f.exists() else {}


def mk(lang):
    def t(en, yue=None):
        if yue is not None:
            REGISTRY[en] = yue
        if lang == "en":
            return en
        if lang == "yue":
            return yue if yue is not None else STR["yue"].get(en, en)
        v = STR[lang].get(en)
        if v is None:
            MISSING.setdefault(lang, set()).add(en)
            return en
        return v
    return t


# ---- prices (content/prices.json, the single source)
PRICES = json.loads((ROOT / "content" / "prices.json").read_text())


def price_text(lang):
    p = PRICES["langs"][lang]
    main = p["main"]
    return f"{main} ({PRICES['usd']})" if main else PRICES["usd"]


def price_html(lang, per):
    p = PRICES["langs"][lang]
    if p["main"]:
        return f'{p["main"]} <mark class="usd">{PRICES["usd"]}</mark> <small>{per}</small>'
    return f'<mark class="usd">{PRICES["usd"]}</mark> <small>{per}</small>'


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


# ---- short interface strings for every language (header, footer, menu)
UI = {
    "skip": {"en": "Skip to content", "zh-hant": "跳到主要內容", "yue": "跳至內容", "zh-hans": "跳到主要内容", "ja": "本文へ移動", "es": "Saltar al contenido", "de": "Zum Inhalt springen", "fr": "Aller au contenu"},
    "signin": {"en": "Sign in", "zh-hant": "登入", "yue": "登入", "zh-hans": "登录", "ja": "ログイン", "es": "Iniciar sesión", "de": "Anmelden", "fr": "Se connecter"},
    "start": {"en": "Start free", "zh-hant": "免費開始", "yue": "免費開始", "zh-hans": "免费开始", "ja": "無料で始める", "es": "Empezar gratis", "de": "Kostenlos starten", "fr": "Commencer gratuitement"},
    "language": {"en": "Language", "zh-hant": "語言", "yue": "語言", "zh-hans": "语言", "ja": "言語", "es": "Idioma", "de": "Sprache", "fr": "Langue"},
    "bigger": {"en": "Bigger text", "zh-hant": "放大文字", "yue": "大字", "zh-hans": "放大文字", "ja": "文字を大きく", "es": "Texto más grande", "de": "Größere Schrift", "fr": "Texte plus grand"},
    "n_practice": {"en": "Practice", "zh-hant": "練習", "yue": "練習", "zh-hans": "练习", "ja": "練習", "es": "Práctica", "de": "Üben", "fr": "Pratique"},
    "n_how": {"en": "How it works", "zh-hant": "運作方式", "yue": "運作方式", "zh-hans": "运作方式", "ja": "しくみ", "es": "Cómo funciona", "de": "So funktioniert's", "fr": "Comment ça marche"},
    "n_plans": {"en": "Plans", "zh-hant": "方案", "yue": "方案", "zh-hans": "方案", "ja": "プラン", "es": "Planes", "de": "Tarife", "fr": "Offres"},
    "n_faq": {"en": "FAQ", "zh-hant": "常見問題", "yue": "常見問題", "zh-hans": "常见问题", "ja": "よくある質問", "es": "Preguntas", "de": "Fragen", "fr": "Questions"},
    "f_privacy": {"en": "Privacy", "zh-hant": "隱私政策", "yue": "私隱政策", "zh-hans": "隐私政策", "ja": "プライバシー", "es": "Privacidad", "de": "Datenschutz", "fr": "Confidentialité"},
    "f_terms": {"en": "Terms", "zh-hant": "使用條款", "yue": "使用條款", "zh-hans": "使用条款", "ja": "利用規約", "es": "Términos", "de": "Nutzungsbedingungen", "fr": "Conditions d’utilisation"},
    "f_safety": {"en": "Privacy and safety", "zh-hant": "隱私與安全", "yue": "私隱與安全", "zh-hans": "隐私与安全", "ja": "プライバシーと安全", "es": "Privacidad y seguridad", "de": "Datenschutz und Sicherheit", "fr": "Confidentialité et sécurité"},
    "f_how": {"en": "How it works", "zh-hant": "運作方式", "yue": "運作方式", "zh-hans": "运作方式", "ja": "しくみ", "es": "Cómo funciona", "de": "So funktioniert's", "fr": "Comment ça marche"},
    "f_ther": {"en": "For therapists", "zh-hant": "給治療師", "yue": "俾治療師", "zh-hans": "给治疗师", "ja": "セラピストの方へ", "es": "Para terapeutas", "de": "Für Therapeuten", "fr": "Pour les thérapeutes"},
    "f_blog": {"en": "Blog", "zh-hant": "部落格", "yue": "網誌", "zh-hans": "博客", "ja": "ブログ", "es": "Blog", "de": "Blog", "fr": "Blog"},
    "f_contact": {"en": "Contact", "zh-hant": "聯絡我們", "yue": "聯絡我哋", "zh-hans": "联系我们", "ja": "お問い合わせ", "es": "Contacto", "de": "Kontakt", "fr": "Contact"},
    "hello": {"en": "Bonet says hello", "zh-hant": "柯基向你打招呼", "yue": "朱古力同你打招呼", "zh-hans": "柯基向你打招呼", "ja": "コーギーがあいさつします", "es": "Bonet te saluda", "de": "Bonet sagt Hallo", "fr": "Bonet vous dit bonjour"},
}
u = lambda k, lang: UI[k][lang]


def head(lang, title, desc, canon, og, extra="", alt=None, app_css=True):
    hl = ""
    if alt:  # alt: dict lang -> absolute url
        hl = "".join(f'<link rel="alternate" hreflang="{LANGS[c]["tag"]}" href="{url}">\n' for c, url in alt.items())
        hl += f'<link rel="alternate" hreflang="x-default" href="{alt["en"]}">\n'
    return f"""<!DOCTYPE html>
<html lang="{LANGS.get(lang, LANGS['en'])['html']}"{f' data-site-lang="{lang}"' if alt else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#1f8ae6">
<script src="/js/boot.js"></script>
<link rel="canonical" href="{canon}">
{hl}<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:site_name" content="Bonet">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/img/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/img/{og}">
<link rel="preload" href="/fonts/nunito-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css">
{'<link rel="stylesheet" href="/css/demos.css">' if app_css else ''}
{extra}<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script defer src="/js/gtag-init.js"></script>
</head>
"""


def lang_menu(cur, urls=None, inplace=None):
    """One compact menu: <details> works without JS. urls: lang -> href for this page (default: the language's home).
    inplace: set of langs that switch text in the same page (inner pages hold English and Cantonese)."""
    items = ""
    for c, d in LANGS.items():
        href = (urls or {}).get(c, d["path"])
        cur_attr = ' aria-current="true"' if c == cur else ""
        if inplace and c in inplace:
            items += f'<li><button type="button" data-setlang="{c}" lang="{d["html"]}"{cur_attr}>{d["name"]}</button></li>'
        else:
            items += f'<li><a href="{href}" hreflang="{d["tag"]}" lang="{d["html"]}"{cur_attr}>{d["name"]}</a></li>'
    return (f'<details class="langmenu"><summary aria-label="{u("language", cur if cur in LANGS else "en")}"><img src="/img/icons/globe.webp" width="128" height="128" alt="">'
            f'<span>{LANGS[cur]["name"]}</span></summary><ul>{items}</ul></details>')


def header(lang, urls=None, inplace=None):
    t = lambda k: u(k, lang)
    pre = LANGS[lang]["path"]
    nav = [(pre + "#how", t("n_practice")), ("/science.html", t("n_how")), (pre + "#plans", t("n_plans")), (pre + "#faq", t("n_faq"))]
    links = "".join(f'<a href="{h}">{x}</a>' for h, x in nav)
    return f"""<body>
<a class="skip" href="#main">{t('skip')}</a>
<header class="hdr"><div class="wrap">
<a class="brand" href="{pre}" aria-label="Bonet"><img src="/img/mascot/head.webp" width="512" height="512" alt="">Bonet{'<small>哥基健動</small>' if lang in ('zh-hant', 'yue', 'zh-hans') else ''}</a>
<nav class="nav" aria-label="Main">{links}</nav>
{lang_menu(lang, urls, inplace)}
<button type="button" class="tsize" data-textsize aria-pressed="false" title="{t('bigger')}" aria-label="{t('bigger')}">A+</button>
<a class="signin" href="{APP}/">{t('signin')}</a>
<a class="btn btn--sm" href="{APP}/">{t('start')}</a>
</div></header>
"""


def footer(lang, urls=None, inplace=None, demos=False):
    t = lambda k: u(k, lang)
    items = [("/privacy.html", "f_privacy"), ("/terms.html", "f_terms"), ("/compliance.html", "f_safety"), ("/science.html", "f_how"),
             ("/therapist.html", "f_ther"), ("/blog/", "f_blog"), (f"mailto:{MAIL}", "f_contact")]
    nav = "".join(f'<a href="{h}">{t(k)}</a>' for h, k in items)
    plain = "".join(f'<a href="{(urls or {}).get(c, d["path"])}" hreflang="{d["tag"]}" lang="{d["html"]}">{d["name"]}</a>' for c, d in LANGS.items())
    return f"""<footer class="ftr"><div class="wrap">
<div class="ftr-pup"><button type="button" class="pupbtn" data-sprite="sleep" data-hover="wiggle" aria-label="{t('hello')}"><span class="sprite" data-clip="sleep" data-rest="sleep" aria-hidden="true"></span></button></div>
<nav aria-label="Footer">{nav}</nav>
<nav class="ftr-langs" aria-label="{t('language')}">{plain}</nav>
<p>&copy; 2026 Coglix Labs Inc.</p>
</div></footer>
<script defer src="/js/site.js"></script>
{'<script defer src="/js/demos.js"></script>' if demos else ''}
</body>
</html>
"""
