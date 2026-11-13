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
const figP: Record<string, Promise<Fig>> = {}
const loadFig = (name: string) => (figP[name] ||= fetch(`/img/figure/${name}.json`).then((r) => r.json()))

type S = { run: boolean; t0: number; reps: number; chip: string; fin: boolean; boom: number; how: boolean; drawn: number; m: number; tip: boolean; cut: boolean }
const S0: S = { run: false, t0: 0, reps: 0, chip: '', fin: false, boom: 0, how: false, drawn: 0, m: 0, tip: false, cut: false }
const J = (f: Fig, n: string) => f.joints.indexOf(n)
const BONES: [string, string][] = [['head', 'neck'], ['neck', 'l_shoulder'], ['neck', 'r_shoulder'], ['l_shoulder', 'l_elbow'], ['l_elbow', 'l_wrist'], ['r_shoulder', 'r_elbow'], ['r_elbow', 'r_wrist'], ['l_shoulder', 'l_hip'], ['r_shoulder', 'r_hip'], ['l_hip', 'r_hip'], ['l_hip', 'l_knee'], ['l_knee', 'l_ankle'], ['r_hip', 'r_knee'], ['r_knee', 'r_ankle']]

function useFrame(run: boolean, t0: number, still: number, name: string) {
  const reduced = useReducedMotion()
  const [fig, setFig] = useState<Fig | null>(null)
  const [k, setK] = useState(0)
  const box = useRef<HTMLDivElement>(null)
  const vis = useRef(true)
  useEffect(() => { loadFig(name).then(setFig) }, [name])
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

function Figure({ w, run, t0, mirror = false, skeleton = false, sheet = 'armraise' }: { w: number; run: boolean; t0: number; mirror?: boolean; skeleton?: boolean; sheet?: string }) {
  const { fig, k, box } = useFrame(run, t0, 16, sheet)
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
      <div style={{ position: 'absolute', inset: 0, backgroundImage: `url(/img/figure/${sheet}.webp)`, backgroundSize: `${fig.cols * 100}% ${fig.rows * 100}%`, backgroundPosition: sheetPos(fig, k), backgroundRepeat: 'no-repeat' }} />
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

const chip: React.CSSProperties = { position: 'absolute', padding: '6px 14px', borderRadius: 14, background: '#fff', border: '2px solid #cfe6fb', color: '#0f4f8f', fontWeight: 900, fontSize: 17, lineHeight: 1.1, whiteSpace: 'nowrap', boxShadow: '0 6px 16px -8px rgba(20,60,110,.35)' }

/* Staging: the person (left, side-on, facing the phone) and the phone on a small stand (right, turned a little towards the person).
   The phone shows what its camera sees: the same person from the front, with the skeleton, count and feedback. The preview is mirrored like a
   selfie (the working arm is on the right of the picture, as it is in a mirror), and the caption "Camera view of you" says what it is. */
function Screen({ s, w }: { s: S; w: number }) {
  return (
    <Phone width={w}>
      <div className="bn-screen" style={{ background: '#fff' }}>
        <div className="bn-top"><span className="bn-brand" style={{ fontSize: 22 }}><Ico n="muscle" s={32} />{t('Arm raise')}</span><span className="bn-chip"><Roll>{`${s.reps}/3`}</Roll></span></div>
        <div style={{ position: 'absolute', left: 12, right: 12, top: 128, height: 640, borderRadius: 24, background: '#eef3f8', overflow: 'hidden', display: 'grid', placeItems: 'center' }}>
          <Figure w={400} run={s.run} t0={s.t0} skeleton />
          <div className="bn-fchip" data-on={!!s.chip || undefined} key={s.chip} style={{ fontSize: 26 }}>{s.chip}</div>
        </div>
        <div className="bn-cue" style={{ position: 'absolute', left: 16, top: 784, right: 16 }}><span className="ok" data-on={s.fin || undefined} style={{ fontSize: 26 }}>{t('Great set!')}</span></div>
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
  )
}

/* A phone drawn side-on / three-quarter, turned to the left towards the person, on a small stand. Its camera dot is on the face that looks at the person. */
function AngledPhone({ x, y }: { x: number; y: number }) {
  return (
    <div style={{ position: 'absolute', left: x, top: y, width: 110, height: 236, perspective: 520 }}>
      <div style={{ width: 110, height: 236, borderRadius: 22, background: 'linear-gradient(90deg,#0f1f33,#2a3a50)', border: '5px solid #46566d', boxShadow: '0 18px 30px -12px rgba(15,31,51,.5)', transform: 'rotateY(-62deg)', transformOrigin: 'center' }}>
        <div style={{ position: 'absolute', inset: 6, borderRadius: 16, background: '#16263c' }} />
      </div>
    </div>
  )
}

const connector = (x1: number, y1: number, x2: number, y2: number) => <path d={`M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}`} fill="none" stroke="#1f8ae6" strokeWidth="2.5" strokeDasharray="2 8" strokeLinecap="round" opacity=".8" />

export function FigureDemo() {
  return (
    <Stage<S> className="bn" width={680} height={640} compact={{ below: 520, width: 358, height: 900 }} initial={S0}
      poster={{ ...S0, reps: 3, fin: true, how: false, drawn: 6, m: 1, tip: true }} script={script}>
      {(s, _r, layout) => {
        const wide = layout === 'wide'
        return (
          <div style={{ position: 'absolute', inset: 0 }}>
            {wide ? (
              <>
                <svg width="680" height="640" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} aria-hidden>
                  <defs><linearGradient id="fov" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stopColor="#1f8ae6" stopOpacity=".3" /><stop offset="1" stopColor="#1f8ae6" stopOpacity=".05" /></linearGradient></defs>
                  <polygon points="352,372 236,70 236,590" fill="url(#fov)" />
                  <line x1="352" y1="372" x2="236" y2="70" stroke="#1f8ae6" strokeWidth="2.5" strokeDasharray="2 9" strokeLinecap="round" opacity=".7" />
                  <line x1="352" y1="372" x2="236" y2="590" stroke="#1f8ae6" strokeWidth="2.5" strokeDasharray="2 9" strokeLinecap="round" opacity=".7" />
                  <ellipse cx="150" cy="580" rx="120" ry="14" fill="#0f4f8f" opacity=".16" />
                  <path d="M392,560 L372,600 M412,560 L440,600" stroke="#46566d" strokeWidth="6" strokeLinecap="round" /><rect x="340" y="598" width="110" height="12" rx="6" fill="#1468b8" opacity=".5" />
                  <circle cx="352" cy="372" r="6" fill="#fff" stroke="#1f8ae6" strokeWidth="3" />
                  {connector(420, 330, 458, 330)}
                </svg>
                <div style={{ position: 'absolute', left: -30, top: 90, transform: 'scaleX(-1)' }}><Figure w={380} run={s.run} t0={s.t0} sheet="armraise-side" /></div>
                <div style={{ ...chip, left: 100, top: 22 }}>{t('You')}</div>
                <div style={{ ...chip, left: 246, top: 278, fontSize: 15 }}>{t("Your phone's camera")}</div>
                <AngledPhone x={330} y={322} />
                <div style={{ ...chip, left: 460, top: 0 }}>{t('What the camera sees')}</div>
                <div style={{ position: 'absolute', left: 430, top: 46 }}><Screen s={s} w={246} /></div>
              </>
            ) : (
              <>
                <svg width="358" height="900" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }} aria-hidden>
                  <defs><linearGradient id="fov2" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stopColor="#1f8ae6" stopOpacity=".3" /><stop offset="1" stopColor="#1f8ae6" stopOpacity=".05" /></linearGradient></defs>
                  <polygon points="236,200 130,30 130,330" fill="url(#fov2)" />
                  <ellipse cx="100" cy="330" rx="80" ry="9" fill="#0f4f8f" opacity=".16" />
                  <circle cx="236" cy="200" r="5" fill="#fff" stroke="#1f8ae6" strokeWidth="3" />
                  <path d="M270,330 L270,372" stroke="#1f8ae6" strokeWidth="3" strokeDasharray="2 8" strokeLinecap="round" />
                </svg>
                <div style={{ position: 'absolute', left: -10, top: 20, transform: 'scaleX(-1)' }}><Figure w={220} run={s.run} t0={s.t0} sheet="armraise-side" /></div>
                <div style={{ ...chip, left: 12, top: 0, fontSize: 15 }}>{t('You')}</div>
                <div style={{ position: 'absolute', left: 226, top: 96, transform: 'scale(.62)', transformOrigin: 'top left' }}><AngledPhone x={0} y={0} /></div>
                <div style={{ ...chip, left: 196, top: 250, fontSize: 14 }}>{t("Your phone's camera")}</div>
                <div style={{ ...chip, left: 54, top: 346, fontSize: 15 }}>{t('What the camera sees')}</div>
                <div style={{ position: 'absolute', left: 54, top: 388 }}><Screen s={s} w={250} /></div>
              </>
            )}
          </div>
        )
      }}
    </Stage>
  )
}
