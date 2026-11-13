#!/usr/bin/env python3
"""Static checks for the animated demos (run: python3 scripts/check-demos.py). Fails (exit 1) when:
  1. a key in content/demo-strings.json lacks a non-empty translation for any of the eight languages, or a non-English value equals the English key (unless allow-listed);
  2. content/demo-speak.json lacks a language, or has too few tiles/hints;
  3. a t('...') call in demos/src/*.tsx uses a key that is not in the dictionary;
  4. a demo component contains hard-coded text (JSX text or a string literal passed to a text/alt/aria prop) that does not go through t() / the content files.
The rendered check (scripts/check-demos.mjs) then loads every language page and compares what the demos actually show."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
LANGS = ["en", "zh-hant", "yue", "zh-hans", "ja", "es", "de", "fr"]
ALLOW_SAME = {"L/R", "OK", "+1", "Bonet", "Y"}          # may equal the English key in another language
ALLOW_PAIR = {("Start", "de"), ("Pauses", "fr")}         # real words in that language too
ALLOW_TEXT = {"Bonet", "app.bonet.care", "+1", "✕", "?", "min"}   # brand, URL, symbols
errs = []
D = json.loads((ROOT / "content" / "demo-strings.json").read_text())
for k, v in D.items():
    for l in LANGS[1:]:
        x = v.get(l)
        if not x: errs.append(f"demo-strings: '{k}' has no {l}")
        elif x == k and k not in ALLOW_SAME and (k, l) not in ALLOW_PAIR and l != "yue": errs.append(f"demo-strings: '{k}' in {l} is still English")
S = json.loads((ROOT / "content" / "demo-speak.json").read_text())
for l in LANGS:
    e = S.get(l)
    if not e: errs.append(f"demo-speak: missing {l}"); continue
    if not (4 <= len(e["words"]) <= 6) or not e["decoy"] or len(e["hints"]) != 3: errs.append(f"demo-speak: {l} needs 4-6 words, a decoy and 3 hints")
    if l not in ("en",) and e["words"] == S["en"]["words"]: errs.append(f"demo-speak: {l} words equal English")
for f in sorted((ROOT / "demos" / "src").glob("*.tsx")):
    if f.name in ("main.tsx", "ui.tsx"): continue
    s = f.read_text()
    for m in re.finditer(r"\bt\((['\"])(.*?)\1\)", s):
        if m.group(2) not in D: errs.append(f"{f.name}: t('{m.group(2)}') is not in demo-strings.json")
    body = re.sub(r"/\*.*?\*/", "", s, flags=re.S); body = re.sub(r"(?m)^\s*//.*$", "", body)
    for m in re.finditer(r">([^<>{}\n]*[A-Za-zÀ-ɏ぀-鿿][^<>{}\n]*)<", body):
        txt = m.group(1).strip()
        if txt and txt not in ALLOW_TEXT and not re.search(r"[():=;]", txt): errs.append(f"{f.name}: hard-coded text '{txt}'")
    for m in re.finditer(r"\b(?:alt|aria-label|title|placeholder)=\"([^\"]+)\"", body):
        if m.group(1).strip(): errs.append(f"{f.name}: hard-coded attribute text '{m.group(1)}'")
if errs:
    print("\n".join(errs)); print(f"{len(errs)} problem(s)"); sys.exit(1)
print("demo strings OK:", len(D), "keys x", len(LANGS), "languages")
