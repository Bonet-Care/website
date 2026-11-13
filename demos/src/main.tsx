import { createRoot } from 'react-dom/client'
import './bonet.css'
import { QualityMove, QualitySpeak } from './Quality'
import { FigureDemo } from './FigureDemo'
import { WebApp } from './WebApp'
import { Hero, MoveCard } from './Move'
import { StreakTile, LeagueTile, WardrobeTile, ProgressTile, LangTile, SimpleTile } from './Bento'
import { SpeakCard, HintCard, BrainCard } from './Cards'

const registry: Record<string, (p: { pq: boolean }) => JSX.Element> = { hero: (p) => <Hero pq={p.pq} />, qmove: QualityMove, qspeak: QualitySpeak, web: WebApp, move: FigureDemo, speak: SpeakCard, hint: HintCard, brain: BrainCard, streak: StreakTile, league: LeagueTile, wardrobe: WardrobeTile, progress: ProgressTile, lang: LangTile, simple: SimpleTile }
document.querySelectorAll<HTMLElement>('[data-demo]').forEach((el) => {
  const C = registry[el.dataset.demo!]
  if (!C) return
  el.textContent = ''
  createRoot(el).render(<C pq={el.dataset.pq === '1'} />)
})
