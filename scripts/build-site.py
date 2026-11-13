#!/usr/bin/env python3
"""
Builds every HTML page of https://bonet.care.

  python3 scripts/build-site.py              build everything
  python3 scripts/build-site.py --export     write strings/source.json (English -> Cantonese gloss) for translators
  python3 scripts/build-site.py --strict     fail if a language file lacks a string
  python3 scripts/build-site.py --strict-fragments   also fail while a long page (legal, science, therapist) has no translation file
  python3 scripts/build-site.py --without practice_quality   leave out sections that need the practice-quality feature
  python3 scripts/build-site.py --with new_demo_video  show the demo film section (default: content/flags.json new_demo_video, false)

Inputs: scripts/home.py (home template, English text with a Cantonese gloss), strings/<lang>.json (English -> language),
content/prices.json, content/*.html (inner pages), content/blog/*.html (posts), content/flags.json.

Every page except the blog is built once per language: English at /<page>, the others at /<lang>/<page> (parts.LOCAL_PAGES).
Short pages (/what-bonet-tracks, /example-report, /compare.html, 404) use the string files, and so do the search landing pages in
scripts/seo_pages.py (four need pages, /compare/bonet-vs-<product>, and /llms.txt) and the practice library in scripts/practice_pages.py
(/practice and the pages under it, generated from content/practice.json, which scripts/extract-practice.py writes from the app's own data). The search titles and descriptions of /science,
/therapist, /faq and /safety are in seo_pages.META (string files again); the meta.<lang>.json files are only the fallback for other pages. Long pages use translated fragments:
content/legal/<slug>.<lang>.html, content/science.<lang>.html, content/therapist.<lang>.html, titles in content/legal/meta.<lang>.json.
While a fragment is missing, the page is still built at the language's URL with the English text (canonical points at the English
page, no hreflang) and the build prints "TRANSLATION PENDING". The translation is picked up as soon as the file exists.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parts
from parts import LANGS, ROOT, SITE, footer, head, header, esc, MISSING, PENDING, REGISTRY, u, pre, localise, page_urls

FLAGS_OFF = set(sys.argv[sys.argv.index("--without") + 1].split(",")) if "--without" in sys.argv else set()
if not json.loads((ROOT / "content" / "flags.json").read_text()).get("practice_quality_live", True):
    FLAGS_OFF.add("practice_quality")
parts.FLAGS_OFF = FLAGS_OFF
import home as homemod  # noqa: E402
import cost as costmod  # noqa: E402
import seo_pages  # noqa: E402
import practice_pages  # noqa: E402
_flags = json.loads((ROOT / "content" / "flags.json").read_text())
homemod.VIDEO_ON = bool(_flags.get("new_demo_video", False)) or ("--with" in sys.argv and "new_demo_video" in sys.argv[sys.argv.index("--with") + 1].split(","))

LASTMOD = "2026-11-13"
write = lambda rel, text: ((ROOT / rel).parent.mkdir(parents=True, exist_ok=True), (ROOT / rel).write_text(text))
out_path = lambda lang, page: f"{pre(lang).strip('/')}/{page}".lstrip("/")  # "privacy.html" -> "ja/privacy.html"

# ---------------------------------------------------------------- inner pages: content/<slug>.html, translated in content/<slug>.<lang>.html
INNER = {
    "science": ("How Bonet works", "運作方式 | 哥基健動", "How Bonet's camera, speaking and brain practice work, what it measures, and what it does not claim.", "science.html", "science"),
    "therapist": ("For therapists and carers | Bonet", "俾治療師同照顧者 | 哥基健動", "How therapists, carers and family can see what someone practised in Bonet, and what the app does not do.", "therapist.html", "therapist"),
}

# ---------------------------------------------------------------- legal pages (English text, translations for convenience) and localised notice pages
# Fragments are in content/legal/<slug>.html (reviewed text, no draft notes). Every open question is listed in LEGAL-PUBLISH-NOTES.md.
LEGAL = {
    "privacy": ("Privacy Policy | Bonet", "What the Bonet app and this website collect, what stays on your device, who else receives data, and how to delete your account.", "0.4"),
    "terms": ("Terms of Service | Bonet", "The terms for using Bonet, a home practice app for movement, speaking and brain games, made by Coglix Labs Inc.", "0.4"),
    "subscriptions": ("Subscriptions and refunds | Bonet", "How Bonet Premium billing works: the free trial, renewal, how to cancel, and how to ask for a refund.", "0.4"),
    "cookies": ("Cookie Policy | Bonet", "What Bonet and this website store on your device, which of it is optional, and how to change your choice.", "0.4"),
    "consumer-health-data": ("Consumer Health Data Privacy Policy | Bonet", "What health-related data Bonet handles, why, who receives it, and your choices under US state consumer health data laws.", "0.3"),
    "ai-and-automatic-measures": ("How Bonet measures | Bonet", "How Bonet's automatic measures work, where they are processed, and their limits.", "0.5"),
}
NOTICES = ("safety", "faq")
NOTICE_META = {}
for _c in LANGS:
    _f = ROOT / "content" / "pages" / f"meta.{_c}.json"
    if _f.exists():
        for _slug, _v in json.loads(_f.read_text()).items():
            NOTICE_META.setdefault(_slug, {})[_c] = _v


# Titles and descriptions of the translated long pages: content/legal/meta.<lang>.json = {"privacy": [title, description], ..., "science": [...], "therapist": [...]}
FRAG_META = {}
for _c in LANGS:
    _f = ROOT / "content" / "legal" / f"meta.{_c}.json"
    if _f.exists():
        FRAG_META[_c] = json.loads(_f.read_text())

# Shown at the top of every translated legal page. {a} wraps the link to the English page.
TRANSLATION_NOTE = {
    "yue": "呢個係方便你閱讀嘅翻譯版本。如果同英文版有出入，以{a}英文版{/a}為準。",
    "zh-hant": "本頁是為了方便閱讀而提供的翻譯。如與英文版有出入，以{a}英文版{/a}為準。",
    "zh-hans": "本页是为了方便阅读而提供的翻译。如与英文版有出入，以{a}英文版{/a}为准。",
    "ja": "このページは参考のための翻訳です。英語版と内容が異なる場合は、{a}英語版{/a}が適用されます。",
    "es": "Esta es una traducción para tu comodidad. Si hay alguna diferencia, se aplica la {a}versión en inglés{/a}.",
    "de": "Dies ist eine Übersetzung zum leichteren Lesen. Bei Abweichungen gilt die {a}englische Fassung{/a}.",
    "fr": "Cette page est une traduction fournie pour votre confort. En cas de différence, la {a}version anglaise{/a} s’applique.",
}


def untranslated(folder, slug):
    """Languages that have no translated fragment for this page yet."""
    return {c for c in LANGS if c != "en" and not (folder / f"{slug}.{c}.html").exists()}


def frag_meta(lang, slug, title, desc):
    v = FRAG_META.get(lang, {}).get(slug)
    if not v:
        PENDING.setdefault(lang, set()).add(f"title:{slug}")
        return title, desc
    return v[0], v[1]


def legal(slug, lang="en"):
    title, desc, _ = LEGAL[slug]
    d = ROOT / "content" / "legal"
    if not (d / f"{slug}.html").exists():
        if lang == "en":
            print("skipped (no fragment):", slug)
            MISSING.setdefault("en", set()).add(f"legal:{slug}")
        return
    skip = untranslated(d, slug)
    translated = lang != "en" and lang not in skip
    en_body = (d / f"{slug}.html").read_text()
    body = (d / f"{slug}.{lang}.html").read_text() if translated else en_body
    if translated and body.count("<!--hkd-->") != en_body.count("<!--hkd-->"):
        print(f"WARNING: {slug}.{lang}.html has {body.count('<!--hkd-->')} <!--hkd--> markers, the English page has {en_body.count('<!--hkd-->')}")
    if parts.PRICES.get("checkout_matches") or slug not in parts.PRICES.get("show_hkd_note_on", []):
        body = re.sub(r"<!--hkd-->.*?<!--/hkd-->", "", body, flags=re.S)  # the Hong Kong dollar note goes away once checkout matches the quoted price
    body = body.replace("<!--hkd-->", "").replace("<!--/hkd-->", "")
    assert "CONFIRM" not in body and "draft-note" not in body and 'class="confirm"' not in body, f"unresolved marker in {slug} ({lang})"
    urls, alt = page_urls(slug, skip)
    if translated:
        title, desc = frag_meta(lang, slug, title, desc)
        note = TRANSLATION_NOTE[lang].replace("{a}", f'<a href="/{slug}" hreflang="en" lang="en">').replace("{/a}", "</a>")
        body = f'<p class="tr-note">{note}</p>\n{body}'
    elif lang != "en":
        PENDING.setdefault(lang, set()).add(f"legal:{slug}")
        body = f'<div lang="en">\n{body}\n</div>'
    h = head(lang, title, desc, alt.get(lang, alt["en"]), "og-en.png", app_css=False, alt=alt if lang in alt else None)
    h += header(lang, urls=urls)
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc doc--legal">\n{body}\n</div></div></main>\n'
    h += footer(lang, urls=urls)
    write(out_path(lang, f"{slug}.html"), localise(h, lang))


def notice(slug, lang):
    f = ROOT / "content" / "pages" / f"{slug}.{lang}.html"
    if not f.exists():
        MISSING.setdefault(lang, set()).add(f"page:{slug}")
        return False
    body = f.read_text()
    assert "CONFIRM" not in body, f"marker in {slug}.{lang}"
    title, desc = seo_pages.meta(slug, lang) if slug in seo_pages.META else NOTICE_META[slug][lang]
    pre = LANGS[lang]["path"].rstrip("/")
    path = f"{slug}.html" if lang == "en" else f"{pre.strip('/')}/{slug}.html"
    alt = {c: f"{SITE}{(LANGS[c]['path'].rstrip('/'))}/{slug}" for c in LANGS}
    h = head(lang, title, desc, alt[lang], "og-en.png", app_css=False, alt=alt)
    urls = {c: f"{LANGS[c]['path'].rstrip('/')}/{slug}" for c in LANGS}
    h += header(lang, urls=urls)
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc doc--legal">\n{body}\n</div></div></main>\n'
    h += footer(lang, urls=urls)
    write(path, localise(h, lang))
    return True


def inner(slug, lang="en"):
    title, _ztitle, desc, path, frag = INNER[slug]
    d = ROOT / "content"
    skip = untranslated(d, frag)
    translated = lang != "en" and lang not in skip
    body = (d / (f"{frag}.{lang}.html" if translated else f"{frag}.html")).read_text()
    body = re.sub(r'\s+data-zh="[^"]*"', "", body)  # Cantonese has its own page now; the English page no longer carries it
    body = re.sub(r'href="(?!https?:|mailto:|/|#)([^"]+)"', r'href="/\1"', body)
    urls, alt = page_urls(path, skip)
    if slug in seo_pages.META and (translated or lang == "en"):
        title, desc = seo_pages.meta(slug, lang)
    elif translated:
        title, desc = frag_meta(lang, slug, title, desc)
    if not translated and lang != "en":
        PENDING.setdefault(lang, set()).add(f"page:{slug}")
        body = f'<div lang="en">\n{body}\n</div>'
    h = head(lang, title, desc, alt.get(lang, alt["en"]), "og-en.png", app_css=False, alt=alt if lang in alt else None)
    h += header(lang, urls=urls)
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc">\n{body}\n</div></div></main>\n'
    h += footer(lang, urls=urls)
    write(out_path(lang, path), localise(h, lang))


# ---------------------------------------------------------------- blog
POSTS = ["spaced-practice", "hint-ladder", "camera-on-device", "designed-for-older-adults"]
ZH_POSTS = {"spaced-practice", "hint-ladder"}
BLOGSTR = {
    "en": ("Bonet Blog: how it works and why", "Notes on how Bonet is designed, with the research behind the choices and where the evidence is thin.", "Stories, research and updates", "Notes on what we are building and why.", "Back to the blog", "Read in written Chinese", "The Chinese version of this post is not ready yet. The English one is below."),
    "zh-hant": ("哥基健動部落格：怎麼運作，為什麼這樣設計", "說明哥基健動的設計，以及背後的研究和證據不足之處。", "設計筆記與研究", "我們在做什麼，為什麼這樣做。", "回到部落格", "Read in English", ""),
}


def meta_of(frag):
    t = re.search(r"<!-- title: (.*?) -->", frag).group(1)
    d = re.search(r"<!-- desc: (.*?) -->", frag).group(1)
    return t, d


def post_page(slug, lang):
    suf = "en" if lang == "en" else "zhhant"
    f = ROOT / "content" / "blog" / f"{slug}.{suf}.html"
    frag = f.read_text()
    title, desc = meta_of(frag)
    body = re.sub(r"<!--.*?-->\n?", "", frag)
    en_url = f"{SITE}/blog/{slug}.html"
    zh_url = f"{SITE}/zh-hant/blog/{slug}.html"
    alt = {"en": en_url, "zh-hant": zh_url} if slug in ZH_POSTS else None
    urls = {"en": f"/blog/{slug}.html", "zh-hant": f"/zh-hant/blog/{slug}.html"} if slug in ZH_POSTS else {"en": f"/blog/{slug}.html", "zh-hant": f"/blog/{slug}.html"}
    path = f"blog/{slug}.html" if lang == "en" else f"zh-hant/blog/{slug}.html"
    h = head(lang, title, desc, f"{SITE}/{path}", "og-en.png" if lang == "en" else "og-zh.png", app_css=False)
    if alt:
        h = h.replace("</head>", "".join(f'<link rel="alternate" hreflang="{LANGS[c]["tag"]}" href="{x}">\n' for c, x in alt.items()) + "</head>")
    back = BLOGSTR[lang][4]
    idx = "/blog/" if lang == "en" else "/zh-hant/blog/"
    h += header(lang, urls=urls)
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc"><a class="back" href="{idx}">&larr; {back}</a>\n{body}\n</div></div></main>\n'
    h += footer(lang, urls=urls)
    write(path, localise(h, lang))
    return title, desc, re.search(r"<h1>(.*?)</h1>", body).group(1), re.search(r'class="meta">(.*?)</p>', body).group(1)


def blog_index(lang):
    items = ""
    for slug in POSTS + ["introducing-bonet"]:
        if lang == "zh-hant" and slug not in ZH_POSTS:
            continue
        if slug == "introducing-bonet":
            if lang != "en":
                continue
            items += '<a href="/blog/introducing-bonet.html"><p class="meta">Platform · November 2026 · 2 min read</p><h2>Why We Built Bonet</h2><p>A printed sheet of exercises is easy to put aside. We built Bonet to make daily practice at home easier to start and easier to keep track of.</p></a>'
            continue
        suf = "en" if lang == "en" else "zhhant"
        frag = (ROOT / "content" / "blog" / f"{slug}.{suf}.html").read_text()
        h1 = re.search(r"<h1>(.*?)</h1>", frag).group(1)
        meta = re.search(r'class="meta">(.*?)</p>', frag).group(1)
        dek = re.search(r'</h1><p>(.*?)</p>', frag).group(1)
        href = f"/blog/{slug}.html" if lang == "en" else f"/zh-hant/blog/{slug}.html"
        items += f'<a href="{href}"><p class="meta">{meta}</p><h2>{h1}</h2><p>{dek}</p></a>'
    t, d, h1, sub = BLOGSTR[lang][0], BLOGSTR[lang][1], BLOGSTR[lang][2], BLOGSTR[lang][3]
    path = "blog/index.html" if lang == "en" else "zh-hant/blog/index.html"
    canon = f"{SITE}/blog/" if lang == "en" else f"{SITE}/zh-hant/blog/"
    page = head(lang, t, d, canon, "og-en.png" if lang == "en" else "og-zh.png", app_css=False)
    page = page.replace("</head>", f'<link rel="alternate" hreflang="en" href="{SITE}/blog/">\n<link rel="alternate" hreflang="zh-Hant" href="{SITE}/zh-hant/blog/">\n</head>')
    urls = {"en": "/blog/", "zh-hant": "/zh-hant/blog/"}
    page += header(lang, urls=urls)
    page += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc"><div class="doc-top"><h1>{h1}</h1><p>{sub}</p></div><div class="post-list">{items}</div></div></div></main>\n'
    page += footer(lang, urls=urls)
    write(path, localise(page, lang))


def old_post():
    body = (ROOT / "content" / "blog-introducing-bonet.html").read_text().replace('href="../', 'href="/')
    h = head("en", "Why We Built Bonet: a simple way to practise at home", "Why Coglix Labs built Bonet: a printed sheet of exercises is easy to put aside. Bonet makes daily practice at home easier to start and to keep track of.",
             f"{SITE}/blog/introducing-bonet.html", "og-en.png", app_css=False)
    h += header("en") + f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc">\n{body}\n</div></div></main>\n' + footer("en")
    write("blog/introducing-bonet.html", h)


def compare_page(lang="en"):
    t = parts.mk(lang)
    body = homemod.compare_full(lang)
    urls, alt = page_urls("compare.html")
    title = t("Bonet vs Constant Therapy, Tactus, TalkPath and Flint Rehab", "哥基健動同 Constant Therapy、Tactus、TalkPath、Flint Rehab 比較")
    desc = t("Bonet compared with Constant Therapy, Tactus Therapy, Lingraphica TalkPath, Flint Rehab and a paper handout: features, prices, sources, and what others do better.",
             "哥基健動同 Constant Therapy、Tactus Therapy、Lingraphica TalkPath、Flint Rehab 同紙本講義比較：功能、價錢、資料來源，亦講埋其他產品做得更好嘅地方。")
    one = (f'<section id="one-to-one" class="cost-sources"><h2>{t("One product at a time", "逐個產品比較")}</h2><ul>'
           + "".join(f'<li><a href="{h}">{x}</a></li>' for h, x in seo_pages.vs_links(lang)) + "</ul></section>")
    h = head(lang, title, desc, alt[lang], "og-en.png", app_css=False, alt=alt)
    h += header(lang, urls=urls)
    h += (f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc" style="max-width:none"><div class="doc-top"><h1>{t("How Bonet compares", "同其他方案比較")}</h1>'
          f'<p>{t("Notes and sources behind the short table on the home page.", "主頁嗰個簡表背後嘅附註同來源。")}</p></div>{body}{one}{costmod.cost_sources(lang)}</div></div></main>\n')
    h += footer(lang, urls=urls)
    write(out_path(lang, "compare.html"), localise(h, lang))


def notfound(lang="en"):
    # Cloudflare Pages serves the nearest 404.html going up the folders, so /ja/404.html answers for every missing /ja/... address
    t = parts.mk(lang)
    h = head(lang, t("Page not found | Bonet", "搵唔到呢一頁 | 哥基健動"), t("This page does not exist. Go back to Bonet, the daily home practice app by Coglix Labs Inc.", "呢一頁並不存在。返去哥基健動，Coglix Labs Inc. 嘅每日居家練習 app。"),
             f"{SITE}{pre(lang)}/404.html", "og-en.png", app_css=False, extra='<meta name="robots" content="noindex, follow">\n')
    h += header(lang)
    h += ('<main id="main" class="doc-wrap"><div class="wrap"><div class="err"><img src="/img/mascot/think.webp" width="512" height="512" alt="">'
          f'<h1>{t("We could not find that page", "我哋搵唔到呢一頁")}</h1><p class="lede">{t("It may have moved. Let us take you back to the start.", "佢可能搬咗。等我哋帶你返去開頭。")}</p>'
          f'<a class="btn btn--lg" href="/">{t("Back to Bonet", "返去哥基健動")}</a></div></div></main>\n')
    h += footer(lang)
    write(out_path(lang, "404.html"), localise(h, lang))


try:
    import extra_pages  # optional: scripts/extra_pages.py defines build(ctx) and SITEMAP = [(loc, priority)]
except ImportError:
    extra_pages = None


def sitemap():
    u_ = []

    def url(loc, pri, alts=None, freq="monthly"):
        x = f"  <url>\n    <loc>{SITE}{loc}</loc>\n"
        for tag, href in (alts or []):
            x += f'    <xhtml:link rel="alternate" hreflang="{tag}" href="{href}"/>\n'
        x += f"    <lastmod>{LASTMOD}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>"
        u_.append(x)
    alts = [(d["tag"], SITE + d["path"]) for d in LANGS.values()] + [("x-default", SITE + "/")]
    for d in LANGS.values():
        url(d["path"], "1.0", alts, "weekly")
    for p, pri in [("/blog/", "0.7"), ("/zh-hant/blog/", "0.6"), ("/blog/introducing-bonet.html", "0.5")]:
        url(p, pri)
    for loc, pri in (extra_pages.SITEMAP if extra_pages else []):
        url(loc, pri)

    def local(page, pri, skip=()):  # one entry per language; a language still showing the English text is left out
        _, alt = page_urls(page, skip)
        al = [(LANGS[c]["tag"], href) for c, href in alt.items()] + [("x-default", alt["en"])]
        for c in alt:
            url(alt[c][len(SITE):], pri, al)
    for slug, (_, _, _, path, frag) in INNER.items():
        local(path, "0.8", untranslated(ROOT / "content", frag))
    local("compare.html", "0.5")
    for slug, (_, _, pri) in LEGAL.items():
        local(slug, pri, untranslated(ROOT / "content" / "legal", slug))
    for slug, pri in (extra_pages.LOCAL_SITEMAP if extra_pages else []) + seo_pages.LOCAL_SITEMAP + practice_pages.LOCAL_SITEMAP:
        local(slug, pri)
    for slug in NOTICES:
        local(slug, "0.6")
    for s in POSTS:
        url(f"/blog/{s}.html", "0.6", [("en", f"{SITE}/blog/{s}.html"), ("zh-Hant", f"{SITE}/zh-hant/blog/{s}.html")] if s in ZH_POSTS else None)
        if s in ZH_POSTS:
            url(f"/zh-hant/blog/{s}.html", "0.5")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(u_) + "\n</urlset>\n")


if __name__ == "__main__":
    for lang in LANGS:
        write(out_path(lang, "index.html"), localise(homemod.home(lang), lang))
    for s in POSTS:
        post_page(s, "en")
        if s in ZH_POSTS:
            post_page(s, "zh-hant")
    for lang in LANGS:
        for s in INNER:
            inner(s, lang)
        for s in LEGAL:
            legal(s, lang)
        for s in NOTICES:
            notice(s, lang)
        compare_page(lang)
        notfound(lang)
    if extra_pages:
        extra_pages.build(sys.modules[__name__])
    seo_pages.build(sys.modules[__name__])
    practice_pages.build(sys.modules[__name__])
    blog_index("en"); blog_index("zh-hant"); old_post(); sitemap()
    if "--export" in sys.argv:
        (ROOT / "strings").mkdir(exist_ok=True)
        (ROOT / "strings" / "source.json").write_text(json.dumps(REGISTRY, ensure_ascii=False, indent=1))
        print("exported", len(REGISTRY), "strings")
    for lang, miss in MISSING.items():
        print(f"missing {len(miss)} strings for {lang}")
        if "--verbose" in sys.argv:
            print("\n".join("  " + x for x in sorted(miss)))
    for lang, pend in PENDING.items():  # a translator has not delivered yet: a warning, the English text is shown meanwhile
        print(f"TRANSLATION PENDING ({lang}), English shown for {len(pend)}: {', '.join(sorted(pend))}")
    if "--strict" in sys.argv and MISSING:
        sys.exit(1)
    if "--strict-fragments" in sys.argv and PENDING:
        sys.exit(1)
    print("built")
