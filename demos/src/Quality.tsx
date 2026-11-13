import { useEffect, useRef, useState } from 'react'
import { Stage } from './kit/stage'
import { Phone } from './kit/phone'
import { useReducedMotion } from './kit/reduced-motion'
import type { Act } from './kit/act'
import {Ico, t } from './ui'

/* Practice-quality hexagon. requires_feature: practice_quality (hold from deploy until the app feature ships). Sample data only.
   Pattern: stageshow `chart-scrub` (a shape that draws in on a hairline grid), `subscriptions` (values roll after the cause), `story` (a tip card arrives last). */
export type S = { drawn: number; m: number; tip: boolean; cut: boolean }
const S0: S = { drawn: 0, m: 0, tip: false, cut: false }

function useTween(target: number, ms: number) {
  const reduced = useReducedMotion()
  const [v, setV] = useState(target)
  const from = useRef(target), t0 = useRef(0), raf = useRef(0), cur = useRef(target)
  useEffect(() => {
    if (reduced) { setV(target); cur.current = target; return }
    from.current = cur.current; t0.current = performance.now()
    const step = (now: number) => {
      const k = Math.min(1, (now - t0.current) / (ms * Math.max(0.3, Math.abs(target - from.current) / 6 + 0.4)))
      const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2
      cur.current = from.current + (target - from.current) * (target === 6 || from.current === 6 ? k : e)
      setV(cur.current)
      if (k < 1) raf.current = requestAnimationFrame(step)
    }
    raf.current = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf.current)
  }, [target, ms, reduced])
  return v
}

const C = { x: 150, y: 150, r: 108 }
const pt = (i: number, v: number) => { const a = -Math.PI / 2 + (i * Math.PI) / 3; return [C.x + Math.cos(a) * C.r * v, C.y + Math.sin(a) * C.r * v] as const }
const poly = (vals: number[]) => vals.map((v, i) => pt(i, v).join(',')).join(' ')

export function Hex({ labels, last, today, s }: { labels: string[]; last: number[]; today: number[]; s: S }) {
  const drawn = useTween(s.drawn, 1500)
  const m = useTween(s.m, 1100)
  const cur = today.map((t, i) => (last[i] + (t - last[i]) * m) * Math.max(0, Math.min(1, drawn - i)))
  return (
    <svg viewBox="0 0 300 300" width="100%" aria-hidden>
      {[0.25, 0.5, 0.75, 1].map((k) => <polygon key={k} points={poly([k, k, k, k, k, k])} fill="none" stroke="#e5e7eb" strokeWidth="2" />)}
      {[0, 1, 2, 3, 4, 5].map((i) => <line key={i} x1={C.x} y1={C.y} x2={pt(i, 1)[0]} y2={pt(i, 1)[1]} stroke="#e5e7eb" strokeWidth="2" />)}
      <polygon points={poly(last)} fill="rgba(107,116,132,.12)" stroke="#6b7484" strokeWidth="2.5" strokeDasharray="6 6" opacity={Math.min(1, drawn / 2)} />
      <polygon points={poly(cur)} fill="rgba(31,138,230,.22)" stroke="#1f8ae6" strokeWidth="4" strokeLinejoin="round" />
      {cur.map((v, i) => { const p = pt(i, Math.max(v, 0.02)); return <circle key={i} cx={p[0]} cy={p[1]} r={drawn > i ? 6 : 0} fill="#1f8ae6" /> })}
      {labels.map((l, i) => { const p = pt(i, 1.2); return <text key={i} x={p[0]} y={p[1]} textAnchor="middle" dominantBaseline="middle" fontSize="15" fontWeight="900" fill="#3f4a5a" opacity={drawn > i - 0.3 ? 1 : 0.15}>{l}</text> })}
    </svg>
  )
}

const TURN = 9800  // one card plays about 9.4 s; the pair takes turns, so each waits one turn between its runs
function Card({ title, labels, last, today, tipText, icon, second = false }: { title: string; labels: string[]; last: number[]; today: number[]; tipText: string; icon: string; second?: boolean }) {
  const first = useRef(true)
  const script = async (a: Act<S>) => {
    if (second && first.current) { first.current = false; await a.wait(TURN); await a.snap({ ...S0 }) }
    await a.wait(900); a.put({ drawn: 6 }); await a.wait(2600); a.put({ m: 1 }); await a.wait(1500); a.put({ tip: true }); await a.wait(3800)
    a.put({ cut: true }); await a.wait(350); await a.snap({ ...S0, cut: true }); await a.wait(150); a.put({ cut: false })
    await a.wait(TURN)
  }
  return (
    <Stage<S> className="bn" width={400} height={620} compact={{ below: 400, width: 358, height: 580 }} initial={second ? { drawn: 6, m: 1, tip: true, cut: false } : S0} poster={{ drawn: 6, m: 1, tip: true, cut: false }} script={script}>
      {(s) => (
        <div className="bn-stagebox">
          <Phone width={330}>
            <div className="bn-screen" style={{ background: '#fff' }}>
              <div className="bn-top" style={{ top: 70 }}><span className="bn-brand" style={{ fontSize: 22 }}><Ico n={icon} s={34} />{title}</span></div>
              <div style={{ position: 'absolute', left: 42, right: 42, top: 140 }}><Hex labels={labels} last={last} today={today} s={s} /></div>
              <div style={{ position: 'absolute', left: 24, top: 462, display: 'flex', gap: 18, fontWeight: 800, fontSize: 15, color: '#3f4a5a' }}>
                <span><i style={{ display: 'inline-block', width: 22, height: 5, background: '#1f8ae6', borderRadius: 3, verticalAlign: 'middle', marginRight: 6 }} />{t('Today')}</span>
                <span><i style={{ display: 'inline-block', width: 22, height: 0, borderTop: '4px dashed #6b7484', verticalAlign: 'middle', marginRight: 6 }} />{t('Last time')}</span>
              </div>
              <div className="bn-ann" data-on={s.drawn >= 2 || undefined} style={{ left: 16, top: 112 }}>{t('Six measures')}</div>
              <div className="bn-ann" data-on={s.m >= 1 || undefined} style={{ right: 16, top: 112 }}>{t('Today')}</div>
              <div className="bn-ann" data-on={s.tip || undefined} style={{ left: 24, top: 482 }}>{t('Your next step')}</div>
              <div className="bn-tipcard" data-on={s.tip || undefined}>
                <img src="/img/mascot/point.webp" width={512} height={512} alt="" />
                <div><b>{t('A tip for next time')}</b><p>{tipText}</p></div>
              </div>
              <div className="bn-cut" data-on={s.cut || undefined} style={{ background: '#fff' }} />
            </div>
          </Phone>
        </div>
      )}
    </Stage>
  )
}

export const MOVE_AXES = () => [t('Range'), t('Pace'), t('Steady'), t('L/R'), t('Hold'), t('Done')]
export const MOVE_LAST = [0.6, 0.5, 0.7, 0.55, 0.4, 0.65]
export const MOVE_TODAY = [0.8, 0.7, 0.75, 0.82, 0.65, 0.92]
export const QualityMove = () => <Card title={t('How it went')} icon="muscle"
  labels={[t('Range'), t('Pace'), t('Steady'), t('L/R'), t('Hold'), t('Done')]}
  last={[0.6, 0.5, 0.7, 0.55, 0.4, 0.65]} today={[0.8, 0.7, 0.75, 0.82, 0.65, 0.92]}
  tipText={t('Lift a little higher on your left side.')} />
export const QualitySpeak = () => <Card second title={t('How it went')} icon="speak"
  labels={[t('Heard'), t('No hints'), t('Pace'), t('Pauses'), t('Start time'), t('Steady')]}
  last={[0.55, 0.45, 0.6, 0.5, 0.6, 0.5]} today={[0.85, 0.7, 0.72, 0.8, 0.7, 0.78]}
  tipText={t('Take a breath before long sentences.')} />
