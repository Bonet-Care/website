"""Shared pieces: languages, string lookup, head, header (with the language menu), footer, prices."""
import json
import re
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
PENDING = {}  # lang -> long fragments (legal, science, therapist) with no translation file yet; the English text is shown. A warning, not a --strict failure.
REGISTRY = {}
for code in LANGS:
    f = ROOT / "strings" / f"{code}.json"
    STR[code] = json.loads(f.read_text()) if f.exists() else {}


# ---- pages that exist under every language path (/privacy in English, /ja/privacy in Japanese, and so on)
LOCAL_PAGES = ("privacy", "terms", "subscriptions", "cookies", "consumer-health-data", "ai-and-automatic-measures", "safety", "faq",
               "what-bonet-tracks", "example-report", "compare", "science", "therapist")
# Search landing pages (scripts/seo_pages.py): one per need, and one comparison page per product in scripts/competitors.json.
NEED_PAGES = ("stroke-home-practice", "exercise-app-for-seniors", "speech-practice-at-home", "for-family-and-carers", "rehab-practice-app", "home-exercise-program-app", "brain-games-for-seniors")
VS_PAGES = {"constant-therapy": "Constant Therapy", "tactus-therapy": "Tactus Therapy", "lingraphica-talkpath": "Lingraphica TalkPath", "flint-rehab": "Flint Rehab"}
vs_slug = lambda s: f"compare/bonet-vs-{s}"
LOCAL_PAGES += NEED_PAGES + tuple(vs_slug(s) for s in VS_PAGES)
# Fact pages (scripts/info_pages.py, built by seo_pages.py like the need pages): plain facts AI answers and search engines can quote.
INFO_PAGES = ("about", "camera-rep-counting", "pricing", "home-exercise-tracking", "movement-speech-brain-games", "alzheimers-and-dementia")
LOCAL_PAGES += INFO_PAGES
# The practice library (scripts/practice_pages.py): the hub, one page per body area, exercise, kind of speaking practice and brain game.
_P = json.loads((ROOT / "content" / "practice.json").read_text())
PRACTICE_PAGES = (("practice",) + tuple(f"practice/area/{a['slug']}" for a in _P["areas"]) + tuple(f"practice/move/{e['slug']}" for e in _P["exercises"])
                  + tuple(f"practice/speak/{m['slug']}" for m in _P["speech"]["modes"]) + tuple(f"practice/think/{g['slug']}" for grp in _P["brain"]["groups"] for g in grp["games"]))
LOCAL_PAGES += PRACTICE_PAGES
_LOC = re.compile(r'href="/(?:(%s)(\.html)?)?(#[^"]*)?"(?! hreflang)' % "|".join(LOCAL_PAGES))


def pre(lang):
    """URL prefix of a language: "" for English, "/ja" for Japanese."""
    p = LANGS[lang]["path"] if lang in LANGS else "/"
    return "" if p == "/" else p.rstrip("/")


def localise(html, lang):
    """Point internal links at the page in this language. Links that carry hreflang (language menu, 'English version') are left alone."""
    if lang == "en":
        return html
    p = pre(lang)
    html = re.sub(r'href="/compliance(\.html)?"', 'href="/safety"', html)  # old address of /safety, still used in some fragments
    return _LOC.sub(lambda m: f'href="{p}/{(m.group(1) + (m.group(2) or "")) if m.group(1) else ""}{m.group(3) or ""}"', html)


def page_urls(page, skip=()):
    """(urls, alt) for a page that exists in every language. page: "privacy", "science.html".
    urls: lang -> path for the language menu. alt: lang -> absolute url for hreflang, without the languages in skip."""
    urls = {c: f"{pre(c)}/{page}" for c in LANGS}
    return urls, {c: SITE + urls[c] for c in LANGS if c not in skip}


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
FACTS = json.loads((ROOT / "content" / "facts.json").read_text())  # speaking_levels, exercises, free_exercises


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
    "n_feedback": {"en": "Feedback", "zh-hant": "回饋", "yue": "回饋", "zh-hans": "反馈", "ja": "フィードバック", "es": "Comentarios", "de": "Rückmeldung", "fr": "Retours"},
    "n_compare": {"en": "Compare", "zh-hant": "比較", "yue": "比較", "zh-hans": "比较", "ja": "比較", "es": "Comparar", "de": "Vergleich", "fr": "Comparer"},
    "n_plans": {"en": "Plans", "zh-hant": "方案", "yue": "方案", "zh-hans": "方案", "ja": "プラン", "es": "Planes", "de": "Tarife", "fr": "Offres"},
    "n_faq": {"en": "FAQ", "zh-hant": "常見問題", "yue": "常見問題", "zh-hans": "常见问题", "ja": "よくある質問", "es": "Preguntas", "de": "Fragen", "fr": "Questions"},
    "f_privacy": {"en": "Privacy", "zh-hant": "隱私政策", "yue": "私隱政策", "zh-hans": "隐私政策", "ja": "プライバシー", "es": "Privacidad", "de": "Datenschutz", "fr": "Confidentialité"},
    "f_terms": {"en": "Terms", "zh-hant": "使用條款", "yue": "使用條款", "zh-hans": "使用条款", "ja": "利用規約", "es": "Términos", "de": "Nutzungsbedingungen", "fr": "Conditions d’utilisation"},
    "f_safety": {"en": "Privacy and safety", "zh-hant": "隱私與安全", "yue": "私隱與安全", "zh-hans": "隐私与安全", "ja": "プライバシーと安全", "es": "Privacidad y seguridad", "de": "Datenschutz und Sicherheit", "fr": "Confidentialité et sécurité"},
    "f_how": {"en": "How it works", "zh-hant": "運作方式", "yue": "運作方式", "zh-hans": "运作方式", "ja": "しくみ", "es": "Cómo funciona", "de": "So funktioniert's", "fr": "Comment ça marche"},
    "f_ther": {"en": "For therapists", "zh-hant": "給治療師", "yue": "俾治療師", "zh-hans": "给治疗师", "ja": "セラピストの方へ", "es": "Para terapeutas", "de": "Für Therapeuten", "fr": "Pour les thérapeutes"},
    "f_blog": {"en": "Blog", "zh-hant": "部落格", "yue": "網誌", "zh-hans": "博客", "ja": "ブログ", "es": "Blog", "de": "Blog", "fr": "Blog"},
    "f_contact": {"en": "Contact", "zh-hant": "聯絡我們", "yue": "聯絡我哋", "zh-hans": "联系我们", "ja": "お問い合わせ", "es": "Contacto", "de": "Kontakt", "fr": "Contact"},
    "f_subs": {"en": "Subscriptions and refunds", "zh-hant": "訂閱與退款", "yue": "訂閱同退款", "zh-hans": "订阅与退款", "ja": "購読と返金", "es": "Suscripciones y reembolsos", "de": "Abos und Erstattungen", "fr": "Abonnements et remboursements"},
    "f_cookies": {"en": "Cookies", "zh-hant": "Cookie", "yue": "Cookie", "zh-hans": "Cookie", "ja": "Cookie", "es": "Cookies", "de": "Cookies", "fr": "Cookies"},
    "f_chd": {"en": "Consumer health data", "zh-hant": "消費者健康資料", "yue": "消費者健康資料", "zh-hans": "消费者健康数据", "ja": "消費者の健康データ", "es": "Datos de salud del consumidor", "de": "Gesundheitsdaten", "fr": "Données de santé"},
    "f_ai": {"en": "How Bonet measures", "zh-hant": "Bonet 如何量度", "yue": "Bonet 點樣量度", "zh-hans": "Bonet 如何测量", "ja": "Bonetの測り方", "es": "Cómo mide Bonet", "de": "Wie Bonet misst", "fr": "Comment Bonet mesure"},
    "f_faq": {"en": "FAQ", "zh-hant": "常見問題", "yue": "常見問題", "zh-hans": "常见问题", "ja": "よくある質問", "es": "Preguntas", "de": "Fragen", "fr": "Questions"},
    "f_cset": {"en": "Cookie settings", "zh-hant": "Cookie 設定", "yue": "Cookie 設定", "zh-hans": "Cookie 设置", "ja": "Cookieの設定", "es": "Ajustes de cookies", "de": "Cookie-Einstellungen", "fr": "Réglages des cookies"},
    "f_english": {"en": "English", "zh-hant": "英文", "yue": "英文", "zh-hans": "英文", "ja": "英語", "es": "en inglés", "de": "auf Englisch", "fr": "en anglais"},
    "f_line": {"en": "Daily home practice for movement, speaking and brain games.", "zh-hant": "在家每日練習運動、說話與腦力遊戲。", "yue": "喺屋企每日練習運動、說話同腦力遊戲。", "zh-hans": "在家每日练习运动、说话与脑力游戏。", "ja": "毎日のおうち練習で、運動・話す・脳トレ。", "es": "Práctica diaria en casa: movimiento, habla y juegos mentales.", "de": "Tägliches Üben zu Hause: Bewegung, Sprechen und Denkspiele.", "fr": "Une pratique quotidienne à la maison : mouvement, parole et jeux de cerveau."},
    "f_stroke": {"en": "Home practice after a stroke", "zh-hant": "中風後在家練習", "yue": "中風後喺屋企練習", "zh-hans": "中风后在家练习", "ja": "脳卒中後の自宅練習", "es": "Práctica en casa tras un ictus", "de": "Üben zu Hause nach Schlaganfall", "fr": "S’exercer à la maison après un AVC"},
    "f_seniors": {"en": "Exercise app for seniors", "zh-hant": "長者運動 App", "yue": "長者運動 app", "zh-hans": "长者运动 App", "ja": "シニア向け運動アプリ", "es": "App de ejercicios para mayores", "de": "Übungs-App für Senioren", "fr": "Appli d’exercices pour seniors"},
    "f_speech": {"en": "Speech practice at home", "zh-hant": "在家練習說話", "yue": "喺屋企練習說話", "zh-hans": "在家练习说话", "ja": "自宅で話す練習", "es": "Practicar el habla en casa", "de": "Sprechen üben zu Hause", "fr": "S’exercer à parler à la maison"},
    "f_family": {"en": "For family and carers", "zh-hant": "給家人與照顧者", "yue": "俾家人同照顧者", "zh-hans": "给家人和照顾者", "ja": "ご家族・介助者の方へ", "es": "Para familiares y cuidadores", "de": "Für Angehörige und Pflegende", "fr": "Pour la famille et les aidants"},
    "f_rehab": {"en": "Looking for a rehab app?", "zh-hant": "在找復健 App？", "yue": "搵復康 app？", "zh-hans": "在找康复 App？", "ja": "リハビリ用アプリをお探しですか", "es": "¿Busca una app de rehabilitación?", "de": "Suchen Sie eine Reha-App?", "fr": "Vous cherchez une appli de rééducation ?"},
    "f_hep": {"en": "Home exercise program app", "zh-hant": "居家運動計畫 App", "yue": "居家運動計劃 app", "zh-hans": "居家运动计划 App", "ja": "自宅運動プログラム用アプリ", "es": "App para el programa de ejercicios en casa", "de": "App für das Heimübungsprogramm", "fr": "Appli pour programme d’exercices à domicile"},
    "f_brain": {"en": "Brain games for seniors", "zh-hant": "長者腦力遊戲", "yue": "長者腦力遊戲", "zh-hans": "长者脑力游戏", "ja": "シニア向け脳トレゲーム", "es": "Juegos mentales para mayores", "de": "Denkspiele für Senioren", "fr": "Jeux de réflexion pour seniors"},
    "f_library": {"en": "Practice library", "zh-hant": "練習資料庫", "yue": "練習庫", "zh-hans": "练习库", "ja": "練習ライブラリ", "es": "Biblioteca de práctica", "de": "Übungsbibliothek", "fr": "Bibliothèque de pratique"},
    "hello": {"en": "Bonet says hello", "zh-hant": "柯基向你打招呼", "yue": "朱古力同你打招呼", "zh-hans": "柯基向你打招呼", "ja": "コーギーがあいさつします", "es": "Bonet te saluda", "de": "Bonet sagt Hallo", "fr": "Bonet vous dit bonjour"},
    "f_about": {"en": "About Bonet", "zh-hant": "關於哥基健動", "yue": "關於哥基健動", "zh-hans": "关于哥基健动", "ja": "Bonetについて", "es": "Acerca de Bonet", "de": "Über Bonet", "fr": "À propos de Bonet"},
    "f_camera": {"en": "Camera rep counting", "zh-hant": "鏡頭計算次數", "yue": "鏡頭數次數", "zh-hans": "镜头计算次数", "ja": "カメラで回数を数える", "es": "Conteo de repeticiones con la cámara", "de": "Wiederholungen zählen mit der Kamera", "fr": "Comptage des répétitions par la caméra"},
    "f_pricing": {"en": "Pricing", "zh-hant": "價格", "yue": "價錢", "zh-hans": "价格", "ja": "料金", "es": "Precios", "de": "Preise", "fr": "Tarifs"},
    "f_tracking": {"en": "Home exercise tracking", "zh-hant": "居家練習紀錄", "yue": "居家練習紀錄", "zh-hans": "居家练习记录", "ja": "自宅練習の記録", "es": "Registro de la práctica en casa", "de": "Übungen zu Hause erfassen", "fr": "Suivi de la pratique à domicile"},
    "f_combined": {"en": "Movement, speech and brain games", "zh-hant": "運動、說話與腦力遊戲", "yue": "運動、說話同腦力遊戲", "zh-hans": "运动、说话与脑力游戏", "ja": "運動・発話・脳トレ", "es": "Movimiento, habla y juegos mentales", "de": "Bewegung, Sprechen und Denkspiele", "fr": "Mouvement, parole et jeux de réflexion"},
    "f_dementia": {"en": "Alzheimer's and dementia: for carers", "zh-hant": "阿茲海默症與失智症：給照顧者", "yue": "腦退化症：俾照顧者", "zh-hans": "阿尔茨海默病与认知症：给照顾者", "ja": "アルツハイマー病・認知症：介護する方へ", "es": "Alzhéimer y demencia: para cuidadores", "de": "Alzheimer und Demenz: für Angehörige", "fr": "Alzheimer et démence : pour les aidants"},
}
u = lambda k, lang: UI[k][lang]
NEED_UI = dict(zip(NEED_PAGES, ("f_stroke", "f_seniors", "f_speech", "f_family", "f_rehab", "f_hep", "f_brain")))  # link label of each need page
NEED_UI.update(zip(INFO_PAGES, ("f_about", "f_camera", "f_pricing", "f_tracking", "f_combined", "f_dementia")))  # and of each fact page


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
{extra}<script defer src="/js/consent.js"></script>
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
    nav = [(pre + "#practice", t("n_practice")), (pre + "#feedback", t("n_feedback")), (pre + "#plans", t("n_plans")), (pre + "#compare", t("n_compare")), (pre + "#faq", t("n_faq"))]
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
    pre = globals()["pre"](lang)
    # every page in the footer exists under each language path; the blog is English plus written Chinese
    legal = [("/privacy", "f_privacy"), ("/terms", "f_terms"), ("/subscriptions", "f_subs"), ("/cookies", "f_cookies"),
             ("/consumer-health-data", "f_chd"), ("/safety", "f_safety"), ("/ai-and-automatic-measures", "f_ai"), ("/faq", "f_faq")]
    nav = "".join(f'<a href="{pre}{h}">{t(k)}</a>' for h, k in legal)
    nav += f'<a href="mailto:{MAIL}">{t("f_contact")}</a><button type="button" class="linkbtn" data-consent-open>{t("f_cset")}</button>'
    blog = "/zh-hant/blog/" if lang == "zh-hant" else "/blog/"
    more = "".join(f'<a href="{h}">{t(k)}</a>' for h, k in [(pre + "/science.html", "f_how"), (pre + "/therapist.html", "f_ther"), (pre + "/practice", "f_library")] + [(f"{pre}/{p}", NEED_UI[p]) for p in NEED_PAGES + INFO_PAGES] + [(blog, "f_blog")])
    plain = "".join(f'<a href="{(urls or {}).get(c, d["path"])}" hreflang="{d["tag"]}" lang="{d["html"]}">{d["name"]}</a>' for c, d in LANGS.items())
    return f"""<footer class="ftr"><div class="wrap">
<div class="ftr-top"><a class="brand" href="{pre or '/'}" aria-label="Bonet"><img src="/img/mascot/head.webp" width="512" height="512" alt="">Bonet</a><p>{t('f_line')}</p></div>
<div class="ftr-cols"><nav aria-label="Footer">{nav}</nav>
<nav class="ftr-more" aria-label="Bonet">{more}</nav>
<nav class="ftr-langs" aria-label="{t('language')}">{plain}</nav></div>
<p class="ftr-c">&copy; 2026 <a href="https://coglixlabs.com/">Coglix Labs Inc.</a></p>
</div></footer>
<script defer src="/js/site.js"></script>
{'<script defer src="/js/demos.js"></script>' if demos else ''}
</body>
</html>
"""
