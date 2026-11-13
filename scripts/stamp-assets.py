#!/usr/bin/env python3
"""Add a content hash to every /css/*.css and /js/*.js reference in the built HTML (?v=abc123).
Browsers and Cloudflare cache these files for hours; without the hash, a visitor who came before a
deploy keeps the old stylesheet with the new HTML and sees an unstyled page. Run after build-site.py."""
import hashlib, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parent.parent
cache = {}
def ver(path):
    f = root / path.lstrip('/')
    if not f.is_file(): return None
    if path not in cache: cache[path] = hashlib.sha256(f.read_bytes()).hexdigest()[:10]
    return cache[path]
pat = re.compile(r'((?:href|src)=")(/(?:css|js)/[^"?#]+\.(?:css|js))(?:\?v=[0-9a-f]+)?(")')
n = 0
for html in root.rglob('*.html'):
    if any(p in html.parts for p in ('node_modules', '.git', 'demos')): continue
    s = html.read_text(encoding='utf-8')
    def rep(m):
        v = ver(m.group(2))
        return m.group(0) if v is None else f'{m.group(1)}{m.group(2)}?v={v}{m.group(3)}'
    t = pat.sub(rep, s)
    if t != s: html.write_text(t, encoding='utf-8'); n += 1
print(f'stamped {n} pages, {len(cache)} assets')
