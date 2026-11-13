# Bonet website

This is the public marketing site for Bonet (哥基健動), served at https://bonet.care. Bonet is a home practice app for movement, speaking and brain games, made by Coglix Labs Inc. The web app itself lives in a separate private repo and is served at https://app.bonet.care.

It is plain static HTML and CSS. There is no framework and no build step for deploys, except the home page, which I generate from one Python file so the English and Chinese versions stay in step.

## Layout

- `scripts/build-site.py`: builds every page (`python3 scripts/build-site.py`; `--strict` fails on a missing translation; `--export` writes `strings/source.json`; `--without practice_quality` leaves out the hexagon sections). Python 3, no packages (Pillow only for the one-off asset scripts).
- `scripts/home.py` (home page template; English text with a Cantonese gloss), `scripts/parts.py` (languages, header, language menu, footer, prices), `scripts/competitors.json` (verified comparison facts, November 2026).
- `strings/<lang>.json`: English string to that language, for zh-hant, zh-hans, ja, es, de, fr. Cantonese (`yue`) text sits in the template next to the English. A new string in `home.py` needs an entry in every file or `--strict` fails.
- `content/prices.json`: every price on every page (`checkout_matches` controls the "charged in Hong Kong dollars" note). `content/flags.json`: `practice_quality_live` (true: hexagons, report and "How it went" are on the home page; the committed build is this one), `new_demo_video` (false: the per-language film section is left out), `android_early_access`. `content/facts.json`: speaking levels, exercises, free exercises (quoted in copy as `{levels}`, `{exercises}`, `{free_ex}`; bump them there when the app changes). `content/*.html`: inner page text; `content/blog/`: posts (EN, and zhhant for two).
- `demos/`: React and Stageshow kit source for the animated phone demos. `cd demos && npm install && npm run build` writes `js/demos.js` and `css/demos.css` (committed; Cloudflare needs no build).
- `css/site.css`, `js/site.js` (language menu, sprite player, scroll entrances), `js/boot.js`, `js/gtag-init.js`.
- `img/mascot/anim/`, `img/figure/`: Blender sprite sheets (see `scripts/mascot/README.md`, `scripts/mascot/figure/README.md`). `media/demo/bonet-demo-<lang>.mp4|jpg|vtt`: per-language video, chosen at build time from the files present (English fallback; keep each under 24 MB).
- `index.html`, `zh-hant/`, `yue/`, `zh-hans/`, `ja/`, `es/`, `de/`, `fr/`, inner pages, `blog/`: generated, committed.
- `_headers`, `_redirects`: Cloudflare Pages headers (strict CSP, no inline script) and redirects (`/zh` to `/zh-hant/`).

## Checks

`python3 scripts/check-demos.py` (no dependencies): every demo string exists in all eight languages (`content/demo-strings.json`, `content/demo-speak.json`), every `t('...')` key exists, and no demo component has hard-coded text. `cd demos && npm install && npm run check` also runs `scripts/check-demos.mjs`: it opens each language page in headless Chromium and fails if a demo shows English text on a non-English page or the language menu marks the wrong language (serve the folder on :8124 or pass a base URL). Demo wording lives in `content/demo-strings.json` (keyed by the English text) and `content/demo-speak.json`. German and French labels use the app's wording (app/web/src/lib/i18n.de.ts, i18n.fr.ts) wherever the same screen text exists there; the sentences and labels the app does not have (for example the speaking demo, the tip text and the league names) are our own wording.

## Editing

Change copy in `scripts/home.py` or `content/`, run `python3 scripts/build-site.py --strict`, commit the generated files. Preview: `python3 -m http.server 8000`.

## How it deploys

Cloudflare Pages, connected to this GitHub repo. Every push to `main` deploys.

- Framework preset: None
- Build command: leave empty (the generated home pages are committed)
- Build output directory: `/`
- Custom domains: `bonet.care` and `www.bonet.care`. I redirect `www` to the apex with a Cloudflare redirect rule.

`_headers` sets HSTS, a Content Security Policy, and the other security headers. The CSP allows inline scripts and styles because the older pages still use them; the only third-party hosts are Google Fonts, Google Analytics and Web3Forms (the demo request form). `_redirects` sends the old `/app/*` paths to https://app.bonet.care so old links keep working.

## Analytics and third parties

Google Analytics (GA4) is the only tracker, with IP anonymisation on and no session recording. It is listed in the privacy page. The demo request form posts to Web3Forms. There is no PostHog and no Tailwind CDN script any more.

## Legal

The footer on every page reads "(c) 2026 Coglix Labs Inc." with links to Privacy, Terms and Privacy and safety. Contact addresses are the ones already on the site (hello@ and privacy@ coglixlabs.com).


## Asset versions

After every build run `python3 scripts/stamp-assets.py`. It adds a content hash to the CSS and JS links. Without it, people who visited before a deploy keep the old stylesheet with the new page and see it unstyled.


## Builds and flags

- Committed build (flags from `content/flags.json`, practice quality on, film section off): `python3 scripts/build-site.py --strict && python3 scripts/stamp-assets.py`.
- Fallback without the hexagons and report (the app feature not shipped): `python3 scripts/build-site.py --strict --without practice_quality && python3 scripts/stamp-assets.py`.
- Film section on (founder approval of `media/demo/*`): set `new_demo_video` to true, or build once with `--with new_demo_video`. The `<video>` has `preload="none"`.
- Hong Kong dollar note: `content/prices.json` `show_hkd_note_on` (subscriptions page and the Cantonese page) while `checkout_matches` is false.
- Pricing facts (Free and Premium lists) come from `app/web/src/lib/limits.ts` (free speaking level 3, free exercise ids, brain games on Easy, 7 days of progress, 2-week report) and `Paywall.tsx`; streak, league and outfits are not gated in the app code.
- Checks: `python3 scripts/check-demos.py`, `python3 scripts/check-links.py`, `node scripts/check-demos.mjs [base]`, and `node scripts/check-demo-sync.mjs [base]` (the hero rep counter must follow the clip: `clips/G03.json`; set `PLAYWRIGHT_CORE` / `CHROMIUM` if playwright-core is not installed in `demos/`).
- Competitor prices on /compare were read from each company's own page on 13 November 2026 (`scripts/competitors.json`, `checked`).
