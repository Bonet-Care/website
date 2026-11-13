import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { useReducedMotion } from './kit/reduced-motion'

/* Demo text exists in English and Cantonese only; other language pages show the English demo text. */
export const ZH = typeof document !== 'undefined' && /^(yue|zh-hk)/i.test(document.documentElement.lang)
export const tr = (en: string, zh: string) => (ZH ? zh : en)

export const Ico = ({ n, s, style }: { n: string; s?: number; style?: CSSProperties }) => (
  <span className="bn-ico" style={{ fontSize: s, ...style }} aria-hidden>
    <img src={`/img/icons/${n}.webp`} width={128} height={128} alt="" draggable={false} />
  </span>
)

/** Guide clip. No poster image: the clip fades in over a neutral ground, and under reduced motion it stays paused on its first frame. */
export function Guide({ clip }: { clip: string; poster?: string }) {
  const ref = useRef<HTMLVideoElement>(null)
  const reduced = useReducedMotion()
  const [ready, setReady] = useState(false)
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
