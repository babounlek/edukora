import { useEffect, useRef, useState, type RefObject } from "react"

/**
 * Détecte si le contenu d'un élément est actuellement coupé visuellement (line-clamp
 * ou ellipsis) - un test sur le texte source ne suffit pas, seule la mesure réelle du
 * DOM sait si le rendu à l'écran a effectivement tronqué le contenu (voir EpreuveCard,
 * qui s'en sert pour ne réafficher l'année sous le titre que si celui-ci l'a coupée).
 * Un ResizeObserver retient la mesure à jour au fil des changements de largeur
 * (redimensionnement de fenêtre, apparition d'une scrollbar).
 */
export function useIsTruncated<T extends HTMLElement>(): [RefObject<T | null>, boolean] {
  const ref = useRef<T>(null)
  const [isTruncated, setIsTruncated] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    function mesurer() {
      if (!el) return
      setIsTruncated(el.scrollHeight - el.clientHeight > 1 || el.scrollWidth - el.clientWidth > 1)
    }

    mesurer()
    const observer = new ResizeObserver(mesurer)
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return [ref, isTruncated]
}
