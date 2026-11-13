import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { useReducedMotion } from './kit/reduced-motion'

import DICT from '../../content/demo-strings.json'
import SPEAK from '../../content/demo-speak.json'

/* Every word inside a demo comes from content/demo-strings.json and content/demo-speak.json, in the page's language
   (<html data-site-lang>). There is no fallback to English on other languages: a missing string is logged and caught by scripts/check-demos.py. */
export const LANG: string = (typeof document !== 'undefined' && document.documentElement.getAttribute('data-site-lang')) || 'en'
export const t = (key: string): string => {
  if (LANG === 'en') return key
  const v = (DICT as Record<string, Record<string, string>>)[key]?.[LANG]
  if (!v) { console.error('missing demo string', LANG, key); return key }
  return v
}
const LOCALE: Record<string, string> = { en: 'en', yue: 'zh-HK', 'zh-hant': 'zh-TW', 'zh-hans': 'zh-CN', ja: 'ja', es: 'es', de: 'de', fr: 'fr' }
/** Monday to Sunday initials in the page language (Intl). */
export const weekdays = (): string[] => Array.from({ length: 7 }, (_, i) => new Intl.DateTimeFormat(LOCALE[LANG] || 'en', { weekday: 'narrow' }).format(new Date(2024, 0, 1 + i)))
export const speakData = () => (SPEAK as Record<string, { cjk: boolean; words: string[]; decoy: string; hints: string[] }>)[LANG] || (SPEAK as any).en

export const Ico = ({ n, s, style }: { n: string; s?: number; style?: CSSProperties }) => (
  <span className="bn-ico" style={{ fontSize: s, ...style }} aria-hidden>
    <img src={`/img/icons/${n}.webp`} width={128} height={128} alt="" draggable={false} />
  </span>
)

/** Guide clip. No poster image: the clip fades in over a neutral ground, and under reduced motion it stays paused on its first frame. */
export function Guide({ clip, onVideo }: { clip: string; poster?: string; onVideo?: (v: HTMLVideoElement | null) => void }) {
  const ref = useRef<HTMLVideoElement>(null)
  const reduced = useReducedMotion()
  const [ready, setReady] = useState(false)
  useEffect(() => { onVideo?.(ref.current); return () => onVideo?.(null) }, [onVideo])
  useEffect(() => {
    const v = ref.current
    if (!v || reduced) return
    const io = new IntersectionObserver(([e]) => (e.isIntersecting ? v.play().catch(() => {}) : v.pause()), { threshold: 0.2 })
    io.observe(v)
    return () => io.disconnect()
  }, [reduced])
  return (
    <video ref={ref} muted loop playsInline preload="auto" aria-hidden onLoadedData={() => setReady(true)} style={{ opacity: ready ? 1 : 0, transition: 'opacity .5s' }}>
      <source src={`${clip}.webm#t=0.1`} type="video/webm" />
      <source src={`${clip}.mp4#t=0.1`} type="video/mp4" />
    </video>
  )
}

const COLORS = ['#3cb44b', '#1f8ae6', '#f28c28', '#ffc23d', '#e5484d', '#8b5cf6']
/** Confetti pieces fired from a point; remount (key) to replay. */
export function Confetti({ n = 26, spread = 190, className = 'bn-conf' }: { n?: number; spread?: number; className?: string }) {
  return (
    <div className={className} aria-hidden>
      {Array.from({ length: n }, (_, i) => {
        const a = (i / n) * Math.PI * 2 + (i % 3) * 0.4
        const r = spread * (0.45 + ((i * 37) % 55) / 100)
        return <i key={i} style={{ background: COLORS[i % 6], ['--x' as string]: `${Math.cos(a) * r}px`, ['--y' as string]: `${Math.sin(a) * r * 0.8 - 40}px`, ['--r' as string]: `${(i * 97) % 540}deg`, animationDelay: `${(i % 5) * 20}ms` }} />
      })}
    </div>
  )
}
