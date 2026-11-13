// Asserts the hero demo's rep counter is driven by the guide clip: each increment happens while the clip's arm is at the top
// (clips/G03.json topStart..topEnd, in the loop the counter expects), and "Great set!" only after the third raise is back down (downBy).
// Usage: node scripts/check-demo-sync.mjs [baseUrl]   (serve the folder first; playwright-core from demos/node_modules)
import { createRequire } from 'node:module'
import { readFileSync } from 'node:fs'
const require = createRequire(new URL('../demos/package.json', import.meta.url))
const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core')
const G = JSON.parse(readFileSync(new URL('../clips/G03.json', import.meta.url)))
const base = process.argv[2] || 'http://localhost:8124'
const exe = process.env.CHROMIUM || undefined
const b = await chromium.launch(exe ? { executablePath: exe } : {})
const p = await b.newPage({ viewport: { width: 1280, height: 900 } })
await p.goto(base + '/', { waitUntil: 'load' })
await p.evaluate(() => document.querySelector('.cnb-row .cnb-btn')?.click())
await p.evaluate(() => document.querySelector('[data-demo=hero]').scrollIntoView({ block: 'center' }))
const log = await p.evaluate(async (G) => {
  const out = [], t0 = performance.now(); let last = '', loops = 0, prev = 0, fin = false
  while (performance.now() - t0 < 40000 && !fin) {
    await new Promise((r) => setTimeout(r, 20))
    const v = document.querySelector('[data-demo=hero] video'); if (!v) continue
    if (v.currentTime < prev - 1) loops++; prev = v.currentTime
    const txt = document.querySelector('[data-demo=hero] .bn-reps')?.textContent || ''
    if (txt !== last) { last = txt; out.push({ type: 'reps', txt, ct: v.currentTime, loops }) }
    if (document.querySelector('[data-demo=hero] .bn-cue .ok[data-on]') && !out.some((o) => o.type === 'fin')) { out.push({ type: 'fin', ct: v.currentTime, loops }); fin = true }
  }
  return out
}, G)
await b.close()
let bad = 0
const fail = (m) => { console.error('FAIL', m); bad++ }
const reps = [1, 2, 3].map((i) => log.find((o) => o.type === 'reps' && o.txt === `${i}/3`))
reps.forEach((e, i) => {
  if (!e) return fail(`never reached ${i + 1}/3`)
  if (e.ct < G.topStart - 0.1 || e.ct > G.topEnd + 0.1) fail(`rep ${i + 1} counted at clip time ${e.ct.toFixed(2)}s; the arm is at the top only ${G.topStart}..${G.topEnd}s`)
  if (i && reps[i - 1] && e.loops - reps[i - 1].loops !== 1) fail(`rep ${i + 1} was not exactly one full loop after rep ${i}`)
})
const f = log.find((o) => o.type === 'fin')
if (!f) fail('set never finished')
else if (reps[2] && (f.loops !== reps[2].loops || f.ct < G.downBy - 0.1)) fail(`finished at loop ${f.loops}, clip time ${f.ct.toFixed(2)}s; the third raise is back down only at ${G.downBy}s of its own loop`)
console.log(bad ? 'demo sync FAILED' : 'demo sync OK', JSON.stringify(log.map((o) => [o.type, o.txt, +o.ct.toFixed(2), o.loops])))
process.exit(bad ? 1 : 0)
