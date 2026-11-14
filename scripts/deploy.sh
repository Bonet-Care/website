#!/bin/bash
# Build and publish the website to Cloudflare Pages (project bonet-website, https://bonet.care).
# Usage: bash scripts/deploy.sh            full site (practice-quality sections shown)
#        bash scripts/deploy.sh --hold     hide the practice-quality sections (use while the app has not shipped them)
set -e
cd "$(dirname "$0")/.."
OUT="$(mktemp -d)/site"
mkdir -p "$OUT"
git archive HEAD | tar -x -C "$OUT"
cd "$OUT"
if [ "$1" = "--hold" ]; then python3 scripts/build-site.py --strict --without practice_quality; else python3 scripts/build-site.py --strict; fi
python3 scripts/stamp-assets.py
python3 scripts/check-links.py
export CLOUDFLARE_ACCOUNT_ID=add0c57f626573a6e3d8345d5af252f6
npx --yes wrangler@4 pages deploy . --project-name bonet-website --branch main --commit-dirty=true
python3 scripts/indexnow.py || true
