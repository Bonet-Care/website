#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver; Bing results feed ChatGPT search and Copilot) about every URL in the live sitemap.
The key is public by design: IndexNow checks that https://bonet.care/<key>.txt holds it. Run after a deploy (deploy.sh does)."""
import json, re, sys, urllib.request
SITE = "https://bonet.care"
KEY = "916f53e9ae6a5b150b9390b8296fa2d4"
xml = urllib.request.urlopen(f"{SITE}/sitemap.xml", timeout=30).read().decode()
urls = sorted(set(re.findall(r"<loc>(.*?)</loc>", xml)))
body = json.dumps({"host": "bonet.care", "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        print(f"indexnow: {r.status} for {len(urls)} urls")
except urllib.error.HTTPError as e:
    print(f"indexnow: HTTP {e.code} {e.read()[:200]!r}", file=sys.stderr)
