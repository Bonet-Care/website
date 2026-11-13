#!/usr/bin/env python3
"""
Builds every HTML page of https://bonet.care.

  python3 scripts/build-site.py              build everything
  python3 scripts/build-site.py --export     write strings/source.json (English -> Cantonese gloss) for translators
  python3 scripts/build-site.py --strict     fail if a language file lacks a string
  python3 scripts/build-site.py --without practice_quality   leave out sections that need the practice-quality feature

Inputs: scripts/home.py (home template, English text with a Cantonese gloss), strings/<lang>.json (English -> language),
content/prices.json, content/*.html (inner pages), content/blog/*.html (posts), content/flags.json.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parts
from parts import LANGS, ROOT, SITE, footer, head, header, esc, MISSING, REGISTRY, u

FLAGS_OFF = set(sys.argv[sys.argv.index("--without") + 1].split(",")) if "--without" in sys.argv else set()
if not json.loads((ROOT / "content" / "flags.json").read_text()).get("practice_quality_live", True):
    FLAGS_OFF.add("practice_quality")
parts.FLAGS_OFF = FLAGS_OFF
import home as homemod  # noqa: E402

LASTMOD = "2026-11-13"
write = lambda rel, text: ((ROOT / rel).parent.mkdir(parents=True, exist_ok=True), (ROOT / rel).write_text(text))

# ---------------------------------------------------------------- inner pages (English text with Cantonese in data-zh)
INNER = {
    "science": ("How Bonet works", "運作方式 | 哥基健動", "How Bonet's camera, speaking and brain practice work, what it measures, and what it does not claim.", "science.html", "science"),
    "therapist": ("For therapists and carers | Bonet", "俾治療師同照顧者 | 哥基健動", "How therapists, carers and family can see what someone practised in Bonet, and what the app does not do.", "therapist.html", "therapist"),
}

# ---------------------------------------------------------------- legal pages (English only) and localised notice pages
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


def legal(slug):
    title, desc, _ = LEGAL[slug]
    body = (ROOT / "content" / "legal" / f"{slug}.html").read_text()
    assert "CONFIRM" not in body and "draft-note" not in body and 'class="confirm"' not in body, f"unresolved marker in {slug}"
    h = head("en", title, desc, f"{SITE}/{slug}", "og-en.png", app_css=False)
    h += header("en", inplace=set())
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc doc--legal">\n{body}\n</div></div></main>\n'
    h += footer("en")
    write(f"{slug}.html", h)


def notice(slug, lang):
    f = ROOT / "content" / "pages" / f"{slug}.{lang}.html"
    if not f.exists():
        MISSING.setdefault(lang, set()).add(f"page:{slug}")
        return False
    body = f.read_text()
    assert "CONFIRM" not in body, f"marker in {slug}.{lang}"
    title, desc = NOTICE_META[slug][lang]
    pre = LANGS[lang]["path"].rstrip("/")
    path = f"{slug}.html" if lang == "en" else f"{pre.strip('/')}/{slug}.html"
    alt = {c: f"{SITE}{(LANGS[c]['path'].rstrip('/'))}/{slug}" for c in LANGS}
    h = head(lang, title, desc, alt[lang], "og-en.png", app_css=False, alt=alt)
    urls = {c: f"{LANGS[c]['path'].rstrip('/')}/{slug}" for c in LANGS}
    h += header(lang, urls=urls)
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc doc--legal">\n{body}\n</div></div></main>\n'
    h += footer(lang, urls=urls)
    write(path, h)
    return True


def inner(slug):
    title, ztitle, desc, path, frag = INNER[slug]
    body = (ROOT / "content" / f"{frag}.html").read_text()
    body = re.sub(r'href="(?!https?:|mailto:|/|#)([^"]+)"', r'href="/\1"', body)
    h = head("en", title, desc, f"{SITE}/{path}", "og-en.png", app_css=False, extra=f'<meta name="x-title-zh" content="{esc(ztitle)}">\n')
    h += header("en", inplace={"en", "yue"})
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc">\n{body}\n</div></div></main>\n'
    h += footer("en", inplace={"en", "yue"})
    write(path, h)


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
    write(path, h)
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
    write(path, page)


def old_post():
    body = (ROOT / "content" / "blog-introducing-bonet.html").read_text().replace('href="../', 'href="/')
    h = head("en", "Why We Built Bonet: a simple way to practise at home", "Why Coglix Labs built Bonet: a printed sheet of exercises is easy to put aside. Bonet makes daily practice at home easier to start and to keep track of.",
             f"{SITE}/blog/introducing-bonet.html", "og-en.png", app_css=False)
    h += header("en") + f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc">\n{body}\n</div></div></main>\n' + footer("en")
    write("blog/introducing-bonet.html", h)


def compare_page():
    t = parts.mk("en")
    body = homemod.compare_full("en")
    h = head("en", "How Bonet compares: notes and sources", "The full comparison of Bonet with Constant Therapy, Tactus Therapy, Lingraphica TalkPath, Flint Rehab and a paper handout, with sources and what others do better.", f"{SITE}/compare.html", "og-en.png", app_css=False)
    h += header("en")
    h += f'<main id="main" class="doc-wrap"><div class="wrap"><div class="doc" style="max-width:none"><div class="doc-top"><h1>How Bonet compares</h1><p>Notes and sources behind the short table on the home page.</p></div>{body}</div></div></main>\n'
    h += footer("en")
    write("compare.html", h)


def notfound():
    h = head("en", "Page not found | Bonet", "This page does not exist. Go back to Bonet, the daily home practice app by Coglix Labs Inc.", f"{SITE}/404.html", "og-en.png", app_css=False,
             extra='<meta name="robots" content="noindex, follow">\n')
    h += header("en")
    h += ('<main id="main" class="doc-wrap"><div class="wrap"><div class="err"><img src="/img/mascot/think.webp" width="512" height="512" alt="">'
          '<h1>We could not find that page</h1><p class="lede">It may have moved. Let us take you back to the start.</p>'
          '<a class="btn btn--lg" href="/">Back to Bonet</a></div></div></main>\n')
    h += footer("en")
    write("404.html", h)


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
    for p, pri in [("/science.html", "0.8"), ("/therapist.html", "0.8"), ("/blog/", "0.7"), ("/zh-hant/blog/", "0.6"), ("/blog/introducing-bonet.html", "0.5"), ("/compare.html", "0.5")]:
        url(p, pri)
    for slug, (_, _, pri) in LEGAL.items():
        url(f"/{slug}", pri)
    for loc, pri in (extra_pages.SITEMAP if extra_pages else []):
        url(loc, pri)
    for slug in NOTICES:
        al = [(d["tag"], SITE + d["path"].rstrip("/") + f"/{slug}") for d in LANGS.values()] + [("x-default", f"{SITE}/{slug}")]
        for d in LANGS.values():
            url(d["path"].rstrip("/") + f"/{slug}", "0.6", al)
    for s in POSTS:
        url(f"/blog/{s}.html", "0.6", [("en", f"{SITE}/blog/{s}.html"), ("zh-Hant", f"{SITE}/zh-hant/blog/{s}.html")] if s in ZH_POSTS else None)
        if s in ZH_POSTS:
            url(f"/zh-hant/blog/{s}.html", "0.5")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(u_) + "\n</urlset>\n")


if __name__ == "__main__":
    for lang in LANGS:
        out = home_html = homemod.home(lang)
        write("index.html" if lang == "en" else LANGS[lang]["path"].strip("/") + "/index.html", out)
    for s in INNER:
        inner(s)
    for s in POSTS:
        post_page(s, "en")
        if s in ZH_POSTS:
            post_page(s, "zh-hant")
    for s in LEGAL:
        legal(s)
    for s in NOTICES:
        for lang in LANGS:
            notice(s, lang)
    if extra_pages:
        extra_pages.build(sys.modules[__name__])
    blog_index("en"); blog_index("zh-hant"); old_post(); compare_page(); notfound(); sitemap()
    if "--export" in sys.argv:
        (ROOT / "strings").mkdir(exist_ok=True)
        (ROOT / "strings" / "source.json").write_text(json.dumps(REGISTRY, ensure_ascii=False, indent=1))
        print("exported", len(REGISTRY), "strings")
    for lang, miss in MISSING.items():
        print(f"missing {len(miss)} strings for {lang}")
    if "--strict" in sys.argv and MISSING:
        sys.exit(1)
    print("built")
