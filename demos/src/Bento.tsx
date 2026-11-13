import { Stage } from './kit/stage'
import { Roll } from './kit/motion/Roll'
import { Chart } from './kit/chart'
import type { Act } from './kit/act'
import {Ico, t, weekdays } from './ui'

/* Bento tiles. Pattern: stageshow `bento` (one focal element per tile, copy kept in the page), `subscriptions` (a value rolls after the thing that feeds it),
   `reorder` (rows make room), `chart-scrub` (kit Chart draws in), `kit-extras` (Toggle/Roll). Each loop resets behind a short cut or is reversible by the control itself. */
const SZ = { width: 420, height: 380, compact: { below: 420, width: 358, height: 340 } }
const Cut = ({ on }: { on?: boolean }) => <div className="bn-cut" data-on={on || undefined} />
const loopReset = async <T extends { cut: boolean }>(a: Act<T>, init: T) => { a.put({ cut: true } as Partial<T>); await a.wait(350); await a.snap({ ...init, cut: true } as Partial<T>); await a.wait(150); a.put({ cut: false } as Partial<T>) }

/* Streak calendar with savers */
type SK = { days: string[]; used: boolean; n: number; cut: boolean }
const SK0: SK = { days: ['done', 'done', '', '', '', '', ''], used: false, n: 5, cut: false }
export function StreakTile() {
  const names = weekdays()
  const script = async (a: Act<SK>) => {
    await a.wait(1500); a.put({ days: ['done', 'done', 'save', '', '', '', ''], used: true }); await a.wait(1700)
    a.put({ days: ['done', 'done', 'save', 'done', '', '', ''], n: 6 }); await a.wait(3000)
    await loopReset(a, SK0)
  }
  return (
    <Stage<SK> className="bn" {...SZ} initial={SK0} poster={{ days: ['done', 'done', 'save', 'done', '', '', ''], used: true, n: 6, cut: false }} script={script}>
      {(s) => (
        <div style={{ position: 'absolute', inset: 0 }}>
          <div className="bn-pad" style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <span className="flame"><Ico n="fire" s={64} /></span><div><div className="bn-big"><Roll>{String(s.n)}</Roll></div><div className="bn-lbl">{t('day streak')}</div></div>
          </div>
          <div className="bn-pad" style={{ top: 130 }}>
            <div className="bn-days">{names.map((d, i) => <div key={i} className="bn-day" data-st={s.days[i] || undefined}><i>{s.days[i] === 'save' ? <Ico n="shield" /> : <Ico n="check" />}</i>{d}</div>)}</div>
            <div className="bn-sv"><span className="bn-sv1" data-used={s.used || undefined}><Ico n="shield" /></span><Ico n="shield" />{t('Savers cover a missed day')}</div>
          </div>
          <Cut on={s.cut} />
        </div>
      )}
    </Stage>
  )
}
/* The second saver greys out when used: handled by the data-used attr on the first one */

/* Weekly league */
type LG = { me: number; pts: number; cut: boolean }
const LG0: LG = { me: 3, pts: 190, cut: false }
const ROWS = [{ n: t('Maple'), p: 260, c: '#f28c28' }, { n: t('Pebble'), p: 230, c: '#1f8ae6' }, { n: t('Sunny'), p: 200, c: '#8b5cf6' }, { n: '', p: 190, c: '#3cb44b' }, { n: t('Willow'), p: 150, c: '#e5484d' }]
const SZL = { ...SZ, compact: { ...SZ.compact, height: 380 } }
export function LeagueTile() {
  const script = async (a: Act<LG>) => {
    await a.wait(1800); a.put({ me: 0, pts: 270 }); await a.wait(3800); await loopReset(a, LG0)
  }
  const order = (me: number) => { const o = [0, 1, 2, 4]; o.splice(me, 0, 3); return o } // indexes of ROWS by rank
  return (
    <Stage<LG> className="bn" {...SZL} initial={LG0} poster={{ me: 0, pts: 270, cut: false }} script={script}>
      {(s) => {
        const o = order(s.me)
        return (
          <div style={{ position: 'absolute', inset: 0 }}>
            <div className="bn-pad" style={{ top: 22, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="bn-tier"><Ico n="medal" s={22} />{t('Leaf league')}</span><span className="bn-lbl">{t('This week')}</span>
            </div>
            {ROWS.map((r, i) => {
              const rank = o.indexOf(i); const me = i === 3
              return (
                <div key={i} className="bn-lrow" data-me={me || undefined} style={{ top: 78 + rank * 58, height: 52, transform: 'none', transition: 'top .8s cubic-bezier(.3,.8,.2,1), background .4s, border-color .4s' }}>
                  <span className="rk">{rank + 1}</span><span className="av" style={{ background: r.c }}>{me ? [...t('You')][0].toUpperCase() : [...r.n][0]}</span>
                  <span className="nm">{me ? t('You') : r.n}</span><span className="pt">{me ? <Roll>{String(s.pts)}</Roll> : r.p}</span>
                </div>
              )
            })}
            <Cut on={s.cut} />
          </div>
        )
      }}
    </Stage>
  )
}

/* Wardrobe */
const OUT = [{ id: 'bandana', d: 3, en: 'Blue bandana', zh: '藍色頸巾' }, { id: 'bowtie', d: 7, en: 'Red bow tie', zh: '紅色領結' }, { id: 'cap', d: 14, en: 'Baseball cap', zh: '棒球帽' }, { id: 'crown', d: 100, en: 'Little crown', zh: '小皇冠' }]
export function WardrobeTile() {
  const script = async (a: Act<{ i: number }>) => { for (let i = 1; i <= 4; i++) { await a.wait(1700); a.put({ i: i % 4 }) } }
  return (
    <Stage<{ i: number }> className="bn" {...SZ} initial={{ i: 0 }} poster={{ i: 1 }} script={script}>
      {(s) => (
        <div style={{ position: 'absolute', inset: 0 }}>
          <div className="bn-wd" style={{ top: 20 }}>{OUT.map((o, k) => <img key={o.id} src={`/img/outfits/${o.id}.webp`} width={256} height={256} alt="" data-on={s.i === k || undefined} />)}</div>
          <div className="bn-chips" style={{ top: 260 }}>{OUT.map((o, k) => <div key={o.id} className="bn-oc" data-on={s.i === k || undefined}><img src={`/img/outfits/${o.id}.webp`} width={256} height={256} alt="" />{t('{n} days').replace('{n}', String(o.d))}</div>)}</div>
        </div>
      )}
    </Stage>
  )
}

/* Progress chart */
type PG = { show: boolean; cut: boolean }
export function ProgressTile() {
  const script = async (a: Act<PG>) => { await a.snap({ show: false }); await a.wait(700); a.put({ show: true }); await a.wait(4200); await loopReset(a, { show: false, cut: false }) }
  const days = weekdays()
  return (
    <Stage<PG> className="bn" {...SZ} initial={{ show: false, cut: false }} poster={{ show: true, cut: false }} script={script}>
      {(s) => (
        <div style={{ position: 'absolute', inset: 0 }}>
          <div className="bn-pad" style={{ display: 'flex', alignItems: 'center', gap: 12 }}><Ico n="chart" s={48} /><div><div style={{ fontSize: 24, fontWeight: 900 }}>{t('Your week')}</div><div className="bn-lbl">{t('Minutes practised each day')}</div></div></div>
          <div style={{ position: 'absolute', left: 28, top: 126 }}><Chart data={[6, 10, 0, 12, 9, 14, 11]} kind="bars" width={364} height={170} show={s.show} /></div>
          <div style={{ position: 'absolute', left: 28, right: 28, top: 306, display: 'flex', justifyContent: 'space-between', fontWeight: 900, fontSize: 15, color: '#6b7484', padding: '0 14px' }}>{days.map((d, i) => <span key={i}>{d}</span>)}</div>
          <Cut on={s.cut} />
        </div>
      )}
    </Stage>
  )
}

/* Six languages */
const LANGS = [['English', 'Good morning'], ['廣東話', '早晨'], ['華語（繁體）', '早安'], ['普通话（简体）', '早上好'], ['Español', 'Buenos días'], ['日本語', 'おはようございます'], ['Deutsch', 'Guten Morgen'], ['Français', 'Bonjour']]
export function LangTile() {
  const script = async (a: Act<{ i: number }>) => { for (let i = 1; i <= LANGS.length; i++) { await a.wait(1500); a.put({ i: i % LANGS.length }) } }
  return (
    <Stage<{ i: number }> className="bn" {...SZ} initial={{ i: 0 }} poster={{ i: 1 }} script={script}>
      {(s) => (
        <div style={{ position: 'absolute', inset: 0 }}>
          <div style={{ position: 'absolute', left: 0, right: 0, top: 36, display: 'grid', placeItems: 'center' }}><img src="/img/mascot/wave.webp" width={512} height={512} alt="" style={{ width: 120, height: 120 }} /></div>
          <div className="bn-lang" style={{ top: 160, fontSize: 40 }}><Roll>{LANGS[s.i][1]}</Roll></div>
          <div className="bn-lchips" style={{ top: 236 }}>{LANGS.map((l, k) => <span key={k} data-on={s.i === k || undefined}>{l[0]}</span>)}</div>
        </div>
      )}
    </Stage>
  )
}

/* Simple mode */
export function SimpleTile() {
  const script = async (a: Act<{ on: boolean }>) => { await a.wait(1600); a.put({ on: true }); await a.wait(3600); a.put({ on: false }); await a.wait(800) }
  return (
    <Stage<{ on: boolean }> className="bn" {...SZ} initial={{ on: false }} poster={{ on: true }} script={script}>
      {(s) => (
        <div style={{ position: 'absolute', inset: 0 }}>
          <div className="bn-sm"><span>{t('Simple mode')}</span><span className="bn-sw" data-on={s.on || undefined}><i /></span></div>
          <div className="bn-mini" data-simple={s.on || undefined}>
            <div className="n">
              {[['move', t('Warm up')], ['speak', t('Speaking')], ['brain', t('Brain game')], ['muscle', t('Exercise')], ['star', t('Weekly league')]].map(([i, t]) => <div key={i} className="bn-row"><Ico n={i} />{t}</div>)}
            </div>
            <div className="s"><div className="bn-lbl">{t("Today's practice")}</div><h3>{t('Warm up')}</h3><div className="bn-btn">{t('Start')}</div></div>
          </div>
        </div>
      )}
    </Stage>
  )
}
