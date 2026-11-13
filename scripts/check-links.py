#!/usr/bin/env python3
"""Link check over the built site: internal links and anchors, hreflang reciprocity, sitemap entries exist."""
import re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
ROOT = Path(__file__).resolve().parent.parent
SITE = "https://bonet.care"
EXT = {"app.bonet.care"}

def resolve(path):
    p = unquote(path).split("?")[0]
    cands = [p.lstrip("/")] if not p.endswith("/") else [p.lstrip("/") + "index.html"]
    if not p.endswith("/"):
        cands += [p.lstrip("/") + ".html", p.lstrip("/") + "/index.html"]
    for c in cands:
        f = ROOT / (c or "index.html")
        if f.is_file(): return f
    return None

class P(HTMLParser):
    def __init__(s): super().__init__(); s.links=[]; s.ids=set(); s.alts=[]; s.canon=None
    def handle_starttag(s, t, a):
        a = dict(a)
        if a.get("id"): s.ids.add(a["id"])
        if t == "a" and a.get("href"): s.links.append(a["href"])
        if t == "link" and a.get("rel") == "alternate" and a.get("hreflang"): s.alts.append((a["hreflang"], a["href"]))
        if t == "link" and a.get("rel") == "canonical": s.canon = a["href"]
pages = {}
for f in ROOT.rglob("*.html"):
    rel = f.relative_to(ROOT)
    if rel.parts[0] in ("node_modules", "demos", "content", ".git"): continue
    p = P(); p.feed(f.read_text()); pages[f] = p
bad = []
redirects = {l.split()[0] for l in (ROOT / "_redirects").read_text().splitlines() if l.strip() and not l.startswith("#")}
for f, p in pages.items():
    for h in p.links:
        u = urlparse(h)
        if u.scheme in ("mailto", "tel", "javascript"): continue
        if u.scheme in ("http", "https"):
            if u.netloc == "bonet.care": u = urlparse(u.path + ("#" + u.fragment if u.fragment else ""))
            else: continue
        path = u.path or ("/" + str(f.relative_to(ROOT)))
        if u.path == "": tgt = f
        else:
            if path in redirects or path.rstrip("/") in redirects or path.startswith("/app"): continue
            tgt = resolve(path)
        if tgt is None: bad.append(f"{f.relative_to(ROOT)}: missing target {h}"); continue
        if u.fragment and tgt in pages and u.fragment not in pages[tgt].ids: bad.append(f"{f.relative_to(ROOT)}: missing anchor {h}")
# hreflang reciprocity
for f, p in pages.items():
    for lang, href in p.alts:
        t = resolve(urlparse(href).path)
        if t is None: bad.append(f"{f.relative_to(ROOT)}: hreflang target missing {href}"); continue
        back = [urlparse(x).path.rstrip("/") for _, x in pages[t].alts]
        me = urlparse(p.canon or "").path.rstrip("/")
        if t != f and me not in back: bad.append(f"{f.relative_to(ROOT)}: {href} does not link back")
# sitemap
for loc in re.findall(r"<loc>(.*?)</loc>", (ROOT / "sitemap.xml").read_text()):
    if resolve(urlparse(loc).path) is None: bad.append(f"sitemap: {loc} not built")
print("\n".join(sorted(set(bad))) or "links ok", f"({len(pages)} pages)")
sys.exit(1 if bad else 0)
