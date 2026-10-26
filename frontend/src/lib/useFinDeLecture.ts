import { useEffect, useRef, type RefObject } from "react"

/**
 * Appelle `surFin` une seule fois quand l'élève est arrivé au bout de `cibleRef` (le bas de l'article est dans le champ de
 * vision) ET qu'il est resté au moins `delaiMs` sur la page : arriver en bas d'un coup de pouce n'est pas avoir lu. Un seuil
 * de temps simple, volontairement - le serveur ne peut de toute façon pas vérifier une lecture, d'où des points petits et
 * plafonnés (voir access.views.cours_lu).
 */
export function useFinDeLecture(
  cibleRef: RefObject<HTMLElement | null>,
  { actif, delaiMs = 30_000, surFin }: { actif: boolean; delaiMs?: number; surFin: () => void },
) {
  const surFinRef = useRef(surFin)
  surFinRef.current = surFin

  useEffect(() => {
    if (!actif) return
    let delaiPasse = false
    let fait = false
    let image = 0

    function verifier() {
      image = 0
      if (fait || !delaiPasse) return
      const element = cibleRef.current
      if (!element) return
      const rect = element.getBoundingClientRect()
      if (rect.height > 0 && rect.bottom <= window.innerHeight * 0.95) {
        fait = true
        surFinRef.current()
      }
    }
    function planifier() {
      if (!image) image = requestAnimationFrame(verifier)
    }

    const minuteur = window.setTimeout(() => {
      delaiPasse = true
      verifier()
    }, delaiMs)
    window.addEventListener("scroll", planifier, { passive: true })
    window.addEventListener("resize", planifier)
    return () => {
      window.clearTimeout(minuteur)
      window.removeEventListener("scroll", planifier)
      window.removeEventListener("resize", planifier)
      if (image) cancelAnimationFrame(image)
    }
  }, [cibleRef, actif, delaiMs])
}
