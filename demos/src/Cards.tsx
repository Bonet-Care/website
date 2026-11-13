import { Stage } from './kit/stage'
import { Phone } from './kit/phone'
import { Roll } from './kit/motion/Roll'
import type { Act } from './kit/act'
import { Confetti, Ico, tr, ZH } from './ui'

const REST = { x: 330, y: 500 }
const Head = ({ icon, title, right }: { icon: string; title: string; right?: string }) => (
  <>
    <div className="bn-hd" style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 142, background: '#fff' }} />
    <span className="bn-x">✕</span>
    <span className="bn-title"><Ico n={icon} s={30} />{title}</span>
    {right && <span className="bn-reps">{right}</span>}
  </>
)

/* ---------------- SPEAK: Build the sentence. Pattern: stageshow `payout-flow` + `freeform-drag` (things travel to a measured slot; the payoff holds). ---------------- */
const WORDS = ZH ? ['我', '想', '飲', '杯水', '唔該', '茶'] : ['I', 'want', 'some', 'water', 'please', 'tea']
const W = WORDS.map((w) => (ZH ? 40 + w.length * 26 : 34 + w.length * 13))
const TRAY = [[4, 0, 5], [2, 3, 1]] // indexes shown in the tray, row by row (jumbled; 5 is the decoy)
const SLOTROWS = [[0, 1, 2], [3, 4]]
const G = 12
const rowX = (ids: number[]) => { const tot = ids.reduce((s, i) => s + W[i], 0) + G * (ids.length - 1); let x = (370 - tot) / 2; return ids.map((i) => { const r = x; x += W[i] + G; return [i, r] as const }) }
const SLOT: Record<number, [number, number]> = {}; const TRAYP: Record<number, [number, number]> = {}
SLOTROWS.forEach((r, ri) => rowX(r).forEach(([i, x]) => (SLOT[i] = [x, 104 + ri * 66])))
TRAY.forEach((r, ri) => rowX(r).forEach(([i, x]) => (TRAYP[i] = [x, 250 + ri * 66])))
SLOT[5] = TRAYP[5]

type SS = { placed: number; fb: boolean; boom: number; cut: boolean }
const S0: SS = { placed: 0, fb: false, boom: 0, cut: false }
export function SpeakCard() {
  const script = async (a: Act<SS>) => {
    await a.wait(1000)
    for (let i = 0; i < 5; i++) { await a.click(`w${i}`); a.put({ placed: i + 1 }); await a.wait(700) }
    await a.wait(300); a.put({ fb: true, boom: 1 }); await a.wait(2600)
    a.put({ cut: true }); await a.wait(350); await a.snap({ ...S0, cut: true }); await a.wait(150); a.put({ cut: false }); await a.move(REST); await a.wait(300)
  }
  return (
    <Stage<SS> className="bn" width={400} height={620} compact={{ below: 400, width: 358, height: 580 }} initial={S0}
      poster={{ placed: 5, fb: true, boom: 0, cut: false }} script={script} cursor={{ at: REST, style: 'touch', ripple: true }}>
      {(s) => (
        <div className="bn-stagebox">
          <Phone width={330}>
            <div className="bn-screen" style={{ background: '#f7f8fa' }}>
              <div className="bn-hd" style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 142, background: '#fff' }} />
              <span className="bn-x">✕</span>
              <span className="bn-title"><Ico n="speak" s={30} />{tr('Speaking', '說話')}</span>
              <span className="bn-reps">1 / 8</span>
              <div className="bn-prog"><i style={{ width: '12%' }} /></div>
              <div className="bn-prompt" style={{ height: 380 }}>
                <span className="ph"><Ico n="tea" /></span>
                <h4>{tr('Build the sentence', '砌句子')}</h4>
                <p>{tr('Asking for a drink', '想要飲嘢')}</p>
                {[0, 1, 2, 3, 4].map((i) => <span key={i} className="bn-slot" style={{ left: SLOT[i][0], top: SLOT[i][1], width: W[i] }} />)}
                {WORDS.map((w, i) => {
                  const inn = i < 5 && s.placed > [0, 1, 2, 3, 4].indexOf(i)
                  const [tx, ty] = TRAYP[i]; const [sx, sy] = SLOT[i]
                  return <span key={i} className="bn-tile" data-target={`w${i}`} data-in={inn || undefined} style={{ left: tx, top: ty, width: W[i], transform: inn ? `translate(${sx - tx}px, ${sy - ty}px)` : undefined }}>{w}</span>
                })}
              </div>
              <div className="bn-fb" data-on={s.fb || undefined} style={{ top: 560, height: 200, bottom: 'auto' }}>
                <span className="ok"><Ico n="check" /></span>
                <h5>{tr('Great!', '好呀！')}</h5><p>{tr('Nice one. That is right.', '啱喇，繼續加油。')}</p>
                <div className="bn-btn">{tr('Next', '下一題')}</div>
              </div>
              {s.boom > 0 && <Confetti key={s.boom} className="bn-conf" n={22} spread={150} />}
              <div className="bn-cut" data-on={s.cut || undefined} />
            </div>
          </Phone>
        </div>
      )}
    </Stage>
  )
}

/* ---------------- HINT LADDER. Pattern: stageshow `form-error` / `ai-cards` (one card, the control changes in place; hints open under the button). ---------------- */
type HS = { n: number; cut: boolean }
export function HintCard() {
  const hints = [tr('It is something to drink.', '同飲嘢有關。'), tr('Starts with the letter w.', '第二個字係「水」。'), ZH ? '杯　水' : 'w a t e r']
  const script = async (a: Act<HS>) => {
    await a.wait(1100)
    for (let i = 1; i <= 3; i++) { await a.click('hbtn'); a.put({ n: i }); await a.wait(1500) }
    await a.wait(900); a.put({ cut: true }); await a.wait(350); await a.snap({ n: 0, cut: true }); await a.wait(150); a.put({ cut: false }); await a.move({ x: 300, y: 250 })
  }
  return (
    <Stage<HS> className="bn" width={420} height={300} compact={{ below: 420, width: 358, height: 280 }} initial={{ n: 0, cut: false }} poster={{ n: 3, cut: false }} script={script} cursor={{ at: { x: 300, y: 250 }, style: 'touch', ripple: true }}>
      {(s) => (
        <div style={{ position: 'absolute', inset: 0 }}>
          <div className="bn-hintcard">
            <h4>{tr('Build the sentence', '砌句子')}</h4>
            <div className="bn-lbl">{tr('Asking for a drink', '想要飲嘢')}</div>
            {hints.map((h, i) => (
              <div key={i} className="bn-hcol" data-open={s.n > i || undefined}><div><div className="bn-hint"><span className="n">{i + 1}</span>{i === 2 ? <code>{h}</code> : h}</div></div></div>
            ))}
            <div className="bn-btn bn-btn--2 bn-hbtn" data-target="hbtn" style={{ width: 250 }}><Ico n="bulb" s={26} />{tr('Give me a hint', '俾啲提示')}</div>
          </div>
          <div className="bn-cut" data-on={s.cut || undefined} />
        </div>
      )}
    </Stage>
  )
}

/* ---------------- BRAIN: pairs. Pattern: stageshow `choreography` (retained tracks) + `phone-touch`. ---------------- */
const FACES = ['apple', 'star', 'heart', 'heart', 'apple', 'star']
type BS = { up: number[]; ok: number[]; cut: boolean }
const B0: BS = { up: [], ok: [], cut: false }
export function BrainCard() {
  const script = async (a: Act<BS>) => {
    const flip = async (i: number) => { await a.click(`c${i}`); a.put((s) => ({ up: [...s.up, i] })); await a.wait(650) }
    await a.wait(1000)
    await flip(0); await flip(1); await a.wait(500); a.put({ up: [] }); await a.wait(700)      // a miss: both turn back
    for (const [x, y] of [[0, 4], [1, 5], [2, 3]]) { await flip(x); await flip(y); await a.wait(250); a.put((s) => ({ ok: [...s.ok, x, y] })); await a.wait(600) }
    await a.wait(2000); a.put({ cut: true }); await a.wait(350); await a.snap({ ...B0, cut: true }); await a.wait(150); a.put({ cut: false }); await a.move(REST); await a.wait(300)
  }
  return (
    <Stage<BS> className="bn" width={400} height={560} compact={{ below: 400, width: 358, height: 540 }} initial={B0}
      poster={{ up: [0, 1, 2, 3, 4, 5], ok: [0, 1, 2, 3, 4, 5], cut: false }} script={script} cursor={{ at: REST, style: 'touch', ripple: true }}>
      {(s) => {
        const n = s.ok.length / 2
        return (
          <div className="bn-stagebox">
            <Phone width={330}>
              <div className="bn-screen" style={{ background: '#fff' }}>
                <Head icon="puzzle" title={tr('Find the pairs', '搵相同')} />
                <div className="bn-prog"><i style={{ width: `${(n / 3) * 100}%` }} /></div>
                <div className="bn-mascot" style={{ top: 160, left: 18 }}>
                  <img src="/img/mascot/think.webp" alt="" width={512} height={512} data-on={n < 3 || undefined} />
                  <img src="/img/mascot/cheer.webp" alt="" width={512} height={512} data-on={n === 3 || undefined} />
                </div>
                <div style={{ position: 'absolute', left: 140, top: 190, fontSize: 30, fontWeight: 900 }}><Roll>{String(n)}</Roll> {tr('of 3 pairs', '/ 3 對')}</div>
                <div className="bn-pairs">
                  {FACES.map((f, i) => (
                    <div key={i} className="bn-pc" data-target={`c${i}`} data-up={s.up.includes(i) || s.ok.includes(i) || undefined} data-ok={s.ok.includes(i) || undefined}>
                      <div className="b">?</div><div className="f"><Ico n={f} /></div>
                    </div>
                  ))}
                </div>
                <div className="bn-cut" data-on={s.cut || undefined} />
              </div>
            </Phone>
          </div>
        )
      }}
    </Stage>
  )
}
