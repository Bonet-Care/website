# Bonet website

This is the public marketing site for Bonet (哥基健動), served at https://bonet.care. Bonet is a home practice app for movement, speaking and brain games, made by Coglix Labs Inc. The web app itself lives in a separate private repo and is served at https://app.bonet.care.

It is plain static HTML and CSS. There is no framework and no build step for deploys, except the home page, which I generate from one Python file so the English and Chinese versions stay in step.

## Layout

- `index.html`, `zh/index.html`: home page (English, Traditional Chinese). Generated, do not edit by hand.
- `scripts/build-home.py`: the copy (both languages) and the layout for the home page.
- `partials/head-en.html`, `partials/head-zh.html`: SEO tags, JSON-LD and Google Analytics for the home pages.
- `css/site.css`: styles for the home page.
- `css/tailwind.css`: pre-built Tailwind CSS for the legal, science, therapist and blog pages. Built once, committed (see below).
- `privacy.html`, `terms.html`, `compliance.html` (Privacy and safety), `science.html`, `therapist.html`, `blog/`: content pages.
- `rehab.html`, `speech.html`: tiny redirect pages to the matching screens in the app.
- `_headers`, `_redirects`: Cloudflare Pages security headers and redirects.
- `img/`: logo, partner logos, social share images (`og-en.png`, `og-zh.png`, 1200x630).

## Editing

Home page copy or layout: edit `scripts/build-home.py`, then run

    python3 scripts/build-home.py

and commit the regenerated `index.html` and `zh/index.html`. Python 3 only, no packages.

Other pages are edited directly. If you add new Tailwind classes to them, rebuild the CSS:

    npx tailwindcss@3.4.17 -c tailwind.config.js -i css/tailwind.src.css -o css/tailwind.css --minify

To preview locally: `python3 -m http.server 8000` and open http://localhost:8000/.

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
