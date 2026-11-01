import { useEffect, useRef, useState, type RefObject } from "react"

import { useMediaQuery } from "@/lib/useMediaQuery"

/** Écart maximal des pupilles, en unités du dessin (le visage fait 120 de large). */
const ECART_MAX = 3.2
/** Distance (px) à partir de laquelle le regard est à fond : plus près, il s'adoucit. */
const PORTEE = 140
/** Au repos depuis ce délai (ms), le regard revient au centre. */
const RETOUR_MS = 3000

/**
 * Les yeux de la mascotte suivent le doigt ou le curseur : renvoie le décalage (dx, dy) des pupilles, calculé depuis
 * le centre de l'élément `ref`. Un seul écouteur léger sur la fenêtre, regroupé par image (requestAnimationFrame) ; coupé
 * pour qui a demandé moins de mouvement. Sur téléphone, le regard se pose là où l'élève vient de toucher l'écran.
 */
export function useRegard(ref: RefObject<Element | null>): { dx: number; dy: number } {
  const mouvementReduit = useMediaQuery("(prefers-reduced-motion: reduce)")
  const [regard, setRegard] = useState({ dx: 0, dy: 0 })
  const image = useRef<number | null>(null)
  const repos = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (mouvementReduit || typeof window === "undefined") return
    function viser(e: PointerEvent) {
      if (image.current !== null) return
      image.current = requestAnimationFrame(() => {
        image.current = null
        const boite = ref.current?.getBoundingClientRect()
        if (!boite || boite.width === 0) return
        const vx = e.clientX - (boite.left + boite.width / 2)
        const vy = e.clientY - (boite.top + boite.height / 2)
        const distance = Math.hypot(vx, vy)
        if (distance === 0) return
        const force = Math.min(1, distance / PORTEE) * ECART_MAX
        setRegard({ dx: (vx / distance) * force, dy: (vy / distance) * force * 0.8 })
        if (repos.current) clearTimeout(repos.current)
        repos.current = setTimeout(() => setRegard({ dx: 0, dy: 0 }), RETOUR_MS)
      })
    }
    window.addEventListener("pointermove", viser, { passive: true })
    window.addEventListener("pointerdown", viser, { passive: true })
    return () => {
      window.removeEventListener("pointermove", viser)
      window.removeEventListener("pointerdown", viser)
      if (image.current !== null) cancelAnimationFrame(image.current)
      if (repos.current) clearTimeout(repos.current)
    }
  }, [mouvementReduit, ref])

  return regard
}
