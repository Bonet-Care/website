import { useEffect, useRef, useState } from 'react'
import { Stage } from './kit/stage'
import { Phone } from './kit/phone'
import { Roll } from './kit/motion/Roll'
import { useReducedMotion } from './kit/reduced-motion'
import type { Act } from './kit/act'
import {Confetti, Ico, t } from './ui'
import { Hex, MOVE_AXES, MOVE_LAST, MOVE_TODAY } from './Quality'

/* Move: a mannequin does an arm raise, a phone propped up films it. The skeleton is NOT hand-animated: the joint positions were projected
   from the Blender rig through the render camera (img/figure/armraise.json) and are drawn for the exact frame of the sprite sheet shown.
   Pattern: stageshow `device-pair` (two objects telling one event), `story` (counter rolls when the cause lands), `annotations` (range arc). */
type Fig = { frames: number; fps: number; frameWidth: number; frameHeight: number; cols: number; rows: number; joints: string[]; points: number[][][]; shoulderAngleDeg: number[]; peakFrames: number[] }
let figP: Promise<Fig> | null = null
const loadFig = () => (figP ||= fetch('/img/figure/armraise.json').then((r) => r.json()))

type S = { run: boolean; t0: number; reps: number; chip: string; fin: boolean; boom: number; how: boolean; drawn: number; m: number; tip: boolean; cut: boolean }
const S0: S = { run: false, t0: 0, reps: 0, chip: '', fin: false, boom: 0, how: false, drawn: 0, m: 0, tip: false, cut: false }
const J = (f: Fig, n: string) => f.joints.indexOf(n)
const BONES: [string, string][] = [['head', 'neck'], ['neck', 'l_shoulder'], ['neck', 'r_shoulder'], ['l_shoulder', 'l_elbow'], ['l_elbow', 'l_wrist'], ['r_shoulder', 'r_elbow'], ['r_elbow', 'r_wrist'], ['l_shoulder', 'l_hip'], ['r_shoulder', 'r_hip'], ['l_hip', 'r_hip'], ['l_hip', 'l_knee'], ['l_knee', 'l_ankle'], ['r_hip', 'r_knee'], ['r_knee', 'r_ankle']]

function useFrame(run: boolean, t0: number, still: number) {
  const reduced = useReducedMotion()
  const [fig, setFig] = useState<Fig | null>(null)
  const [k, setK] = useState(0)
  const box = useRef<HTMLDivElement>(null)
  const vis = useRef(true)
  useEffect(() => { loadFig().then(setFig) }, [])
  useEffect(() => {
    const el = box.current; if (!el) return
    const io = new IntersectionObserver(([e]) => (vis.current = e.isIntersecting)); io.observe(el); return () => io.disconnect()
  }, [fig])
  useEffect(() => {
    if (!fig) return
    if (reduced || !run) { setK(reduced ? still : 0); return }
    let raf = 0
    const step = () => { if (vis.current && !document.hidden) setK(Math.floor(((performance.now() - t0) * fig.fps) / 1000) % fig.frames); raf = requestAnimationFrame(step) }
    raf = requestAnimationFrame(step); return () => cancelAnimationFrame(raf)
  }, [fig, run, t0, reduced, still])
  return { fig, k, box }
}

const sheetPos = (f: Fig, k: number) => `${(k % f.cols) / (f.cols - 1) * 100}% ${Math.floor(k / f.cols) / (f.rows - 1) * 100}%`

function Figure({ w, run, t0, mirror = false, skeleton = false }: { w: number; run: boolean; t0: number; mirror?: boolean; skeleton?: boolean }) {
  const { fig, k, box } = useFrame(run, t0, 16)
  const h = w * 1.5
  if (!fig) return <div ref={box} style={{ width: w, height: h }} />
  const P = fig.points[k]
  const ang = fig.shoulderAngleDeg[k]
  const sh0 = fig.points[0][J(fig, 'r_shoulder')]
  const sh = [sh0[0] + 74, sh0[1]] // the arm swings forward, towards the camera, so the angle is shown on a gauge beside the body, not as a sweep of the arm
  const R = 70
  const toRad = (d: number) => (d * Math.PI) / 180
  const arcPt = (d: number) => [sh[0] + R * Math.sin(toRad(d)), sh[1] + R * Math.cos(toRad(d))] // gauge: 0 = arm hanging down, 180 = overhead; shoulderAngleDeg is the true 3D angle from the rig
  const a0 = arcPt(0), a1 = arcPt(Math.max(ang, 1)), tg = arcPt(150)
  return (
    <div ref={box} style={{ position: 'relative', width: w, height: h, transform: mirror ? 'scaleX(-1)' : undefined }}>
      <div style={{ position: 'absolute', inset: 0, backgroundImage: 'url(/img/figure/armraise.webp)', backgroundSize: `${fig.cols * 100}% ${fig.rows * 100}%`, backgroundPosition: sheetPos(fig, k), backgroundRepeat: 'no-repeat' }} />
      {skeleton && (
        <svg viewBox={`0 0 ${fig.frameWidth} ${fig.frameHeight}`} width={w} height={h} style={{ position: 'absolute', inset: 0 }} aria-hidden>
          {BONES.map(([a, b], i) => {
            const pa = P[J(fig, a)], pb = P[J(fig, b)]; const work = a.startsWith('r_') || b.startsWith('r_') && !(a === 'r_hip' && b === 'l_hip')
            return <line key={i} x1={pa[0]} y1={pa[1]} x2={pb[0]} y2={pb[1]} stroke={work ? '#1f8ae6' : '#7fbdf2'} strokeWidth={work ? 7 : 4} strokeLinecap="round" />
          })}
          {P.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r={fig.joints[i].startsWith('r_') && i < 8 ? 7 : 5} fill="#fff" stroke="#1f8ae6" strokeWidth="3" />)}
          <path d={`M${a0[0]},${a0[1]} A${R},${R} 0 0 0 ${a1[0]},${a1[1]}`} fill="none" stroke="#ffc23d" strokeWidth="6" strokeLinecap="round" />
          <circle cx={tg[0]} cy={tg[1]} r="5" fill="none" stroke="#f28c28" strokeWidth="3" strokeDasharray="3 3" />
        </svg>
      )}
    </div>
  )
}

const TOP = 1375, REP = 2667
const script = async (a: Act<S>) => {
  await a.wait(700); a.put({ run: true, t0: performance.now() })
  await a.wait(TOP); a.put({ reps: 1, chip: t('Good height') })
  await a.wait(REP); a.put({ reps: 2, chip: t('A little slower down') })
  await a.wait(REP); a.put({ reps: 3, chip: '+1' })
  await a.wait(1300); a.put({ run: false, chip: '', fin: true, boom: 1 })
  await a.wait(1800); a.put({ how: true, drawn: 0 }); await a.wait(600)
  a.put({ drawn: 6 }); await a.wait(2300); a.put({ m: 1 }); await a.wait(1200); a.put({ tip: true }); await a.wait(2600)
  a.put({ cut: true }); await a.wait(350); await a.snap({ ...S0, cut: true }); await a.wait(150); a.put({ cut: false })
}

export function FigureDemo() {
  return (
    <Stage<S> className="bn" width={660} height={600} compact={{ below: 520, width: 358, height: 560 }} initial={S0}
      poster={{ ...S0, reps: 3, fin: true, how: true, drawn: 6, m: 1, tip: true }} script={script}>
      {(s, _r, layout) => {
        const wide = layout === 'wide'
        return (
          <div style={{ position: 'absolute', inset: 0 }}>
            {wide && (
              <>
                <div style={{ position: 'absolute', left: 24, top: 50 }}><Figure w={300} run={s.run} t0={s.t0} /></div>
                <svg width="660" height="600" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} aria-hidden>
                  <line x1="318" y1="250" x2="392" y2="170" stroke="#1f8ae6" strokeWidth="2" strokeDasharray="2 8" strokeLinecap="round" opacity=".6" />
                  <line x1="318" y1="420" x2="392" y2="520" stroke="#1f8ae6" strokeWidth="2" strokeDasharray="2 8" strokeLinecap="round" opacity=".6" />
                  <rect x="470" y="570" width="140" height="14" rx="7" fill="#1468b8" opacity=".35" />
                </svg>
              </>
            )}
            <div style={{ position: 'absolute', left: wide ? 380 : 14, top: 20 }}>
              <Phone width={wide ? 262 : 330}>
                <div className="bn-screen" style={{ background: '#fff' }}>
                  <div className="bn-top"><span className="bn-brand" style={{ fontSize: 22 }}><Ico n="muscle" s={32} />{t('Arm raise')}</span><span className="bn-chip"><Roll>{`${s.reps}/3`}</Roll></span></div>
                  <div style={{ position: 'absolute', left: 16, right: 16, top: 134, height: 520, borderRadius: 24, background: '#eef3f8', overflow: 'hidden', display: 'grid', placeItems: 'center' }}>
                    <Figure w={346} run={s.run} t0={s.t0} skeleton />{/* not mirrored: the phone shows the figure the same way round as the figure beside it, which is what people expect to see */}
                    <div className="bn-fchip" data-on={!!s.chip || undefined} key={s.chip}>{s.chip}</div>
                  </div>
                  <div className="bn-lock" style={{ top: 672, left: 16, right: 16, height: 52 }}><Ico n="lock" />{t('Stays on your device')}</div>
                  <div className="bn-cue" style={{ position: 'absolute', left: 16, top: 740, right: 16 }}><span className="ok" data-on={s.fin || undefined} style={{ fontSize: 22 }}>{t('Great set!')}</span></div>
                  {s.boom > 0 && <Confetti key={s.boom} n={26} spread={150} className="bn-conf" />}
                  <div className="bn-layer" data-off={!s.how || undefined} style={{ zIndex: 1, background: '#fff' }}>
                    <div className="bn-screen" style={{ background: '#fff' }}>
                      <div className="bn-top"><span className="bn-brand" style={{ fontSize: 22 }}><Ico n="muscle" s={32} />{t('How it went')}</span></div>
                      <div style={{ position: 'absolute', left: 46, right: 46, top: 128 }}><Hex labels={MOVE_AXES()} last={MOVE_LAST} today={MOVE_TODAY} s={{ drawn: s.drawn, m: s.m, tip: s.tip, cut: false }} /></div>
                      <div className="bn-tipcard" data-on={s.tip || undefined} style={{ top: 520 }}><img src="/img/mascot/point.webp" width={512} height={512} alt="" /><div><b>{t('A tip for next time')}</b><p>{t('Lift a little higher on your left side.')}</p></div></div>
                    </div>
                  </div>
                  <div className="bn-cut" data-on={s.cut || undefined} />
                </div>
              </Phone>
            </div>
          </div>
        )
      }}
    </Stage>
  )
}
