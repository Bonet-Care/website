import { Stage } from './kit/stage'
import { Phone } from './kit/phone'
import { Roll } from './kit/motion/Roll'
import type { Act } from './kit/act'
import {Confetti, Guide, Ico, t } from './ui'
import { Hex, MOVE_AXES, MOVE_LAST, MOVE_TODAY } from './Quality'
import G03 from '../../clips/G03.json'

/* The guide clip (clips/G03.mp4, 4 s loop, arm down at 0 s) is the clock: a rep is counted when the video itself reaches the top (G03.topStart)
   and the set ends only after the third raise is back down (G03.downBy). No separate timers decide the count. */
const clock: { v: HTMLVideoElement | null } = { v: null }
const setClockVideo = (v: HTMLVideoElement | null) => { clock.v = v }

/* Pattern: stageshow `phone-touch` (touch cursor, cropped phone, loop that folds back) + `payout-flow` (slow beats, payoff holds). */
type S = { scene: 'today' | 'move' | 'how' | 'back'; reps: number; fin: boolean; cut: boolean; boom: number; drawn: number; m: number; tip: boolean }
const START: S = { scene: 'today', reps: 0, fin: false, cut: false, boom: 0, drawn: 0, m: 0, tip: false }
const REST = { x: 330, y: 470 }
const TOTAL = 3
const NODES = [
  { i: 'move', l: t('Warm up'), x: 128, y: 430 },
  { i: 'speak', l: t('Speaking'), x: 276, y: 540 },
  { i: 'brain', l: t('Brain game'), x: 128, y: 650 },
]

function Today({ done }: { done: boolean }) {
  const st = (i: number) => (i === 0 ? (done ? 'done' : 'cur') : i === 1 && done ? 'cur' : 'locked')
  return (
    <div className="bn-screen">
      <div className="bn-top">
        <span className="bn-brand"><img src="/img/mascot/head.webp" width={512} height={512} alt="" />Bonet</span>
        <span className="bn-chip bn-streak"><span className="flame"><Ico n="fire" s={24} /></span><Roll>{done ? '4' : '3'}</Roll></span>
      </div>
      <div className="bn-mascot">
        <img src="/img/mascot/idle.webp" alt="" data-on={!done || undefined} width={512} height={512} />
        <img src="/img/mascot/cheer.webp" alt="" data-on={done || undefined} width={512} height={512} />
      </div>
      <div className="bn-bub">{done ? t('Well done! One step ticked.') : t('Good morning! Ready for today?')}</div>
      <div className="bn-card bn-goal">
        <Ico n="trophy" />
        <b>{t("Today's goal")}</b>
        <output><Roll>{done ? '1 / 3' : '0 / 3'}</Roll></output>
        <div className="bn-bar"><i style={{ width: done ? '34%' : '0%' }} /></div>
      </div>
      <svg className="bn-path" width="402" height="874" aria-hidden>
        {NODES.slice(0, 2).map((n, i) => (
          <g key={i}>
            <line x1={n.x} y1={n.y} x2={NODES[i + 1].x} y2={NODES[i + 1].y} stroke="#e5e7eb" strokeWidth="8" strokeDasharray="4 14" strokeLinecap="round" />
            {i === 0 && <line x1={n.x} y1={n.y} x2={NODES[1].x} y2={NODES[1].y} stroke="#ffc23d" strokeWidth="8" strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={done ? 0 : 1} style={{ transition: 'stroke-dashoffset .8s ease .35s' }} />}
          </g>
        ))}
      </svg>
      {NODES.map((n, i) => (
        <div key={i}>
          <div className="bn-node" data-target={i === 0 ? 'node' : undefined} data-st={st(i)} style={{ left: n.x, top: n.y }}>
            <Ico n={n.i} /><Ico n="check" />
          </div>
          <div className="bn-lab" data-st={st(i)} style={{ left: n.x + (i % 2 ? -190 : 58), top: n.y - 12, textAlign: i % 2 ? 'right' : 'left' }}>{n.l}</div>
          {st(i) === 'cur' && <div className="bn-start" style={{ left: n.x, top: n.y - 82 }}>{t('START HERE')}</div>}
        </div>
      ))}
    </div>
  )
}

export function Player({ reps, fin, boom }: { reps: number; fin: boolean; boom: number }) {
  return (
    <div className="bn-player">
      <div className="bn-hd" />
      <span className="bn-x">✕</span>
      <span className="bn-title"><Ico n="muscle" s={30} />{t('Arm raise')}</span>
      <span className="bn-reps"><Roll>{`${reps}/${TOTAL}`}</Roll></span>
      <div className="bn-prog"><i style={{ width: `${(reps / TOTAL) * 100}%` }} /></div>
      <div className="bn-guide"><Guide clip="/clips/G03" onVideo={setClockVideo} /></div>
      <div className="bn-sheet">
        <div className="bn-ring">
          <svg width="140" height="140" viewBox="0 0 140 140"><circle cx="70" cy="70" r="60" stroke="#e5e7eb" /><circle className="arc" cx="70" cy="70" r="60" strokeDasharray={`${(reps / TOTAL) * 377} 400`} /></svg>
          <div className="bn-num"><Roll>{String(reps)}</Roll></div>
          {reps > 0 && <div className="bn-plus" key={reps} data-go>+1</div>}
        </div>
        <div className="bn-of">{t('of 3 reps')}</div>
        <div className="bn-cue">
          <span className="gold" data-on={(reps === 2 && !fin) || undefined}>{t('Lift a little higher')}</span>
          <span className="ok" data-on={fin || undefined}>{t('Great set!')}</span>
        </div>
        {boom > 0 && <Confetti key={boom} />}
      </div>
    </div>
  )
}

const script = (full: boolean, pq: boolean) => async (a: Act<S>) => {
  await a.wait(900)
  if (full) {
    a.mark('tap')
    window.dispatchEvent(new CustomEvent('bonet:start'))
    await a.click('node')
    a.put({ scene: 'move' })
    await a.wait(900)
  }
  const v = clock.v
  let loops = 0, prev = 0
  if (v) { v.currentTime = 0; await v.play().catch(() => {}) }
  const tick = () => { const ct = v ? v.currentTime : 0; if (ct < prev - 1) loops++; prev = ct; return ct }
  const until = async (cond: (ct: number) => boolean, max = 20000) => { const t0 = performance.now(); while (performance.now() - t0 < max) { if (cond(tick())) return; await a.wait(30) } }
  if (v) {
    for (let i = 1; i <= TOTAL; i++) { await until((ct) => loops === i - 1 && ct >= G03.topStart); a.put({ reps: i }) }
    await until((ct) => loops === TOTAL - 1 && ct >= G03.downBy)
  } else {
    for (let i = 1; i <= TOTAL; i++) { await a.wait(i === 1 ? 1000 : 4000); a.put({ reps: i }) }
    await a.wait(2000)
  }
  a.put({ fin: true, boom: 1 })
  if (full) window.dispatchEvent(new CustomEvent('bonet:goal'))
  await a.wait(1900)
  if (full && pq) {
    a.put({ scene: 'how' }); await a.wait(700)
    a.put({ drawn: 6 }); await a.wait(2300)
    a.put({ m: 1 }); await a.wait(1300)
    a.put({ tip: true }); await a.wait(2600)
  }
  if (full) {
    a.put({ scene: 'back' })
    await a.wait(3400)
  }
  a.put({ cut: true }) // the day is over: a short cut, then the next morning starts again
  await a.wait(350)
  await a.snap({ ...START, scene: full ? 'today' : 'move', cut: true })
  await a.wait(200)
  a.put({ cut: false })
  await a.move(REST)
  await a.wait(300)
}

const sc = (s: S, full: boolean, pq = false) => (
  <Phone width={330} className="bn-phone">
    {full && <Today done={s.scene === 'back'} />}
    <div className="bn-layer" data-off={(full && s.scene !== 'move') || undefined} style={{ zIndex: 1 }}>
      <Player reps={s.reps} fin={s.fin} boom={s.boom} />
    </div>
    {full && pq && (
      <div className="bn-layer" data-off={s.scene !== 'how' || undefined} style={{ zIndex: 1 }}>
        <div className="bn-screen" style={{ background: '#fff' }}>
          <div className="bn-top"><span className="bn-brand" style={{ fontSize: 24 }}><Ico n="muscle" s={34} />{t('How it went')}</span></div>
          <div style={{ position: 'absolute', left: 46, right: 46, top: 128 }}><Hex labels={MOVE_AXES()} last={MOVE_LAST} today={MOVE_TODAY} s={{ drawn: s.drawn, m: s.m, tip: s.tip, cut: false }} /></div>
          <div style={{ position: 'absolute', left: 24, right: 24, top: 462, fontSize: 16, fontWeight: 800, color: '#3f4a5a', lineHeight: 1.25 }}>{t('After each activity, see how your practice went and get a tip for next time.')}</div>
          <div className="bn-tipcard" data-on={s.tip || undefined} style={{ top: 540 }}><img src="/img/mascot/point.webp" width={512} height={512} alt="" /><div><b>{t('A tip for next time')}</b><p>{t('Lift a little higher on your left side.')}</p></div></div>
        </div>
      </div>
    )}
    <div className="bn-cut" data-on={s.cut || undefined} />
  </Phone>
)

/** Hero: the one core action, Start on Today, counted reps, Great set, back on the path. */
export function Hero({ pq = true }: { pq?: boolean }) {
  return (
    <Stage<S> className="bn" width={400} height={600} compact={{ below: 400, width: 358, height: 560 }} initial={START}
      poster={{ scene: pq ? 'how' : 'back', reps: 3, fin: true, cut: false, boom: 0, drawn: 6, m: 1, tip: true }} script={script(true, pq)}
      cursor={{ at: REST, style: 'touch', ripple: true }}>
      {(s) => <div className="bn-stagebox">{sc(s, true, pq)}</div>}
    </Stage>
  )
}

/** Move feature card: the counting screen alone. */
export function MoveCard() {
  return (
    <Stage<S> className="bn" width={400} height={540} compact={{ below: 400, width: 358, height: 500 }} initial={{ ...START, scene: 'move' }}
      poster={{ scene: 'move', reps: 3, fin: true, cut: false, boom: 0, drawn: 0, m: 0, tip: false }} script={script(false, false)}
      cursor={{ at: REST, style: 'touch' }}>
      {(s) => <div className="bn-stagebox">{sc(s, false)}</div>}
    </Stage>
  )
}
