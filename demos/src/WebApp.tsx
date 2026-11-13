import { Stage } from './kit/stage'
import { Window } from './kit/window'
import { Roll } from './kit/motion/Roll'
import type { Act } from './kit/act'
import { Confetti, Guide, Ico, tr } from './ui'

/* The web app on a big screen: left rail, Today with path + streak, then Move list and player.
   Pattern: stageshow `chrome` (browser Window), `story`/`table-edit` (a click on the rail moves to the next screen), cursor `arrow`. */
type S = { scr: 'today' | 'list' | 'play'; reps: number; fin: boolean; boom: number; cut: boolean }
const S0: S = { scr: 'today', reps: 0, fin: false, boom: 0, cut: false }
const TABS = [['today', tr('Today', '今日')], ['move', tr('Move', '運動')], ['speak', tr('Speak', '說話')], ['brain', tr('Brain', '腦力')], ['me', tr('Me', '我')]]

const script = async (a: Act<S>) => {
  await a.wait(1200)
  await a.click('t-move'); a.put({ scr: 'list' }); await a.wait(1400)
  await a.click('start'); a.put({ scr: 'play' }); await a.wait(1200)
  for (let i = 1; i <= 3; i++) { await a.wait(1200); a.put({ reps: i }) }
  await a.wait(400); a.put({ fin: true, boom: 1 }); await a.wait(2600)
  a.put({ cut: true }); await a.wait(350); await a.snap({ ...S0, cut: true }); await a.wait(150); a.put({ cut: false })
  await a.move({ x: 520, y: 380 }); await a.wait(300)
}

export function WebApp() {
  return (
    <Stage<S> className="bn" width={960} height={600} compact={{ below: 640, width: 640, height: 440 }} initial={S0}
      poster={{ scr: 'play', reps: 3, fin: true, boom: 0, cut: false }} script={script} cursor={{ at: { x: 520, y: 380 }, style: 'arrow', ripple: true }}>
      {(s, _r, layout) => (
        <div style={{ position: 'absolute', inset: 0, padding: layout === 'compact' ? '16px 0 0 16px' : '28px 0 0 36px' }}>
          <Window url="app.bonet.care" urlShape="pill" style={{ width: layout === 'compact' ? 700 : 1000, height: layout === 'compact' ? 520 : 640 }}>
            <div className="bn-web">
              <aside className="bn-rail">
                <img className="bn-rail__logo" src="/img/mascot/head.webp" width={512} height={512} alt="" />
                {TABS.map(([k, l]) => {
                  const on = (k === 'today' && s.scr === 'today') || (k === 'move' && s.scr !== 'today')
                  return <div key={k} className="bn-rail__t" data-target={`t-${k}`} data-on={on || undefined}><Ico n={k === 'today' ? 'today' : k === 'me' ? 'me' : k} s={34} /><span>{l}</span></div>
                })}
              </aside>
              <main className="bn-main">
                <div className="bn-wl" data-off={s.scr !== 'today' || undefined}>
                  <div className="bn-wpath">
                    <div className="bn-wco"><img src="/img/mascot/idle.webp" width={512} height={512} alt="" /><div className="bn-bub2">{tr('Good morning! Ready for today?', '早晨！今日準備好未？')}</div></div>
                    {[['move', tr('Warm up', '熱身'), 0], ['speak', tr('Speaking', '說話'), 1], ['brain', tr('Brain game', '腦力遊戲'), 2]].map(([i, l, k]) => (
                      <div key={String(i)} className="bn-wnode" style={{ marginLeft: (k as number) % 2 ? 90 : 0 }}><span className="bn-wn" data-st={k === 0 ? 'cur' : 'locked'}><Ico n={String(i)} s={38} /></span><b>{l}</b></div>
                    ))}
                  </div>
                  <div className="bn-wside">
                    <div className="bn-card bn-wc"><span className="flame"><Ico n="fire" s={44} /></span><div><div className="bn-big" style={{ fontSize: 42 }}>3</div><div className="bn-lbl">{tr('day streak', '日連續練習')}</div></div></div>
                    <div className="bn-card bn-wc" style={{ display: 'block' }}><b style={{ fontSize: 20 }}>{tr("Today's goal", '今日目標')}</b><div className="bn-wbar"><i style={{ width: '0%' }} /></div></div>
                  </div>
                </div>
                <div className="bn-wl2" data-off={s.scr !== 'list' || undefined}>
                  <h4>{tr('Move', '運動')}</h4>
                  {[[tr('Arm raise', '舉手'), tr('10 times', '10 下'), true], [tr('Sit to stand', '企起坐低'), tr('8 times', '8 下'), false], [tr('Heel raise', '踮腳'), tr('12 times', '12 下'), false]].map(([n, m, go], i) => (
                    <div key={i} className="bn-card bn-wrow"><div className="bn-wth"><Ico n="muscle" s={52} /></div><div><b>{n as string}</b><div className="bn-lbl">{m as string}</div></div><span className="bn-btn" data-target={go ? 'start' : undefined} style={{ minHeight: 46, fontSize: 17, marginLeft: 'auto' }}>{tr('Start', '開始')}</span></div>
                  ))}
                </div>
                <div className="bn-wp" data-off={s.scr !== 'play' || undefined}>
                  <div className="bn-wcam"><Guide clip="/clips/G03" /></div>
                  <div className="bn-wcol">
                    <b style={{ fontSize: 22 }}>{tr('Arm raise', '舉手')}</b>
                    <div className="bn-ring" style={{ position: 'relative', width: 140, height: 140, left: 0, top: 0 }}>
                      <svg width="140" height="140" viewBox="0 0 140 140"><circle cx="70" cy="70" r="60" stroke="#e5e7eb" /><circle className="arc" cx="70" cy="70" r="60" strokeDasharray={`${(s.reps / 3) * 377} 400`} /></svg>
                      <div className="bn-num"><Roll>{String(s.reps)}</Roll></div>
                      {s.reps > 0 && <div className="bn-plus" key={s.reps} data-go>+1</div>}
                    </div>
                    <div className="bn-lbl">{tr('of 3 reps', '共 3 下')}</div>
                    <div className="bn-cue" style={{ position: 'relative', left: 0, top: 0, right: 0 }}><span className="ok" data-on={s.fin || undefined}>{tr('Great set!', '做得好！')}</span></div>
                    {s.boom > 0 && <Confetti key={s.boom} n={30} spread={180} className="bn-conf" />}
                  </div>
                </div>
                <div className="bn-cut" data-on={s.cut || undefined} style={{ background: '#fff' }} />
              </main>
            </div>
          </Window>
        </div>
      )}
    </Stage>
  )
}
