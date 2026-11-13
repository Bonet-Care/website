// Rendered check: loads every language's home page in headless Chromium (reduced motion, so each demo shows its poster frame),
// collects the text each demo shows and fails if a non-English page shows English demo text (a dictionary key or English hint/word) outside the allow-list,
// or if the console reports a missing demo string. Usage: node scripts/check-demos.mjs [baseUrl]   (needs playwright-core: set PLAYWRIGHT_CORE to its folder if it is not installed in demos/)
import { createRequire } from 'node:module'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
const here = dirname(fileURLToPath(import.meta.url)); const root = join(here, '..')
const req = createRequire(join(root, 'demos', 'package.json'))
let pw; try { pw = req(process.env.PLAYWRIGHT_CORE || 'playwright-core') } catch { console.error('playwright-core not found: npm i -D playwright-core in demos/ or set PLAYWRIGHT_CORE'); process.exit(2) }
const base = process.argv[2] || 'http://localhost:8124'
const D = JSON.parse(readFileSync(join(root, 'content', 'demo-strings.json'), 'utf8')); const S = JSON.parse(readFileSync(join(root, 'content', 'demo-speak.json'), 'utf8'))
const PATH = { en: '/', 'zh-hant': '/zh-hant/', yue: '/yue/', 'zh-hans': '/zh-hans/', ja: '/ja/', es: '/es/', de: '/de/', fr: '/fr/' }
const ALLOW = new Set(['Bonet', 'app.bonet.care', '+1', 'L/R', 'OK', 'min'])
const exe = process.env.CHROMIUM || (process.env.HOME + '/Library/Caches/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-mac-arm64/chrome-headless-shell')
const browser = await pw.chromium.launch({ executablePath: exe }); let bad = 0
for (const [lang, path] of Object.entries(PATH)) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' }); const p = await ctx.newPage(); const logs = []
  p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()) })
  await p.goto(base + path); await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 150)) } }); await p.waitForTimeout(1500)
  const texts = await p.evaluate(() => [...document.querySelectorAll('[data-demo]')].map((d) => ({ demo: d.dataset.demo, text: [...d.querySelectorAll('*')].filter((e) => !e.children.length && e.textContent.trim()).map((e) => e.textContent.trim()) })))
  const english = new Set([...Object.keys(D), ...S.en.words, S.en.decoy, ...S.en.hints])
  const issues = []
  if (lang !== 'en') for (const { demo, text } of texts) for (const t of text) { if (english.has(t) && !ALLOW.has(t) && !(D[t] && D[t][lang] === t)) issues.push(`${demo}: English text "${t}"`) }
  for (const l of logs) if (/missing demo string/.test(l)) issues.push(l)
  const lm = await p.evaluate(() => { const c = document.querySelector('.langmenu [aria-current="true"]'); return c ? c.textContent : null })
  const want = { en: 'English', 'zh-hant': '繁體中文', yue: '廣東話', 'zh-hans': '简体中文', ja: '日本語', es: 'Español', de: 'Deutsch', fr: 'Français' }[lang]
  if (lm !== want) issues.push(`language menu marks "${lm}" instead of "${want}"`)
  const links = await p.evaluate(() => [...document.querySelectorAll('.langmenu a')].map((a) => a.getAttribute('href')))
  if (links.length !== 8) issues.push('language menu has ' + links.length + ' entries')
  console.log(lang.padEnd(8), texts.length, 'demos', issues.length ? 'FAIL\n  ' + issues.join('\n  ') : 'ok'); bad += issues.length; await ctx.close()
}
await browser.close(); process.exit(bad ? 1 : 0)
