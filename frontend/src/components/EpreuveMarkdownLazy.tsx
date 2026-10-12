import { Suspense, lazy, useEffect, useRef, useState } from "react"

import { Skeleton } from "@/components/ui/skeleton"

// EpreuveMarkdown embarque react-markdown, le pipeline remark/rehype et KaTeX : environ 180 Ko
// compressés, soit plus que tout le reste de l'accueil. Les extraits de la page d'accueil sont
// sous le pli, donc ce module ne se charge qu'à l'approche de l'extrait (voir plus bas), pas
// avec la page.
const EpreuveMarkdown = lazy(() => import("@/components/EpreuveMarkdown").then((m) => ({ default: m.EpreuveMarkdown })))

interface EpreuveMarkdownLazyProps {
  markdown: string
  directCoursLinks?: boolean
}

/**
 * Même rendu que EpreuveMarkdown, mais différé : à utiliser pour un extrait qui n'est pas
 * visible dès l'arrivée sur la page. Sur les pages de lecture, où le Markdown est le contenu
 * même, importer EpreuveMarkdown directement.
 */
export function EpreuveMarkdownLazy({ markdown, directCoursLinks }: EpreuveMarkdownLazyProps) {
  const repere = useRef<HTMLDivElement>(null)
  const [proche, setProche] = useState(() => typeof IntersectionObserver === "undefined")

  useEffect(() => {
    if (proche) return
    const el = repere.current
    if (!el) return
    // Marge large : le chargement démarre bien avant que l'extrait entre à l'écran.
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setProche(true)
          observer.disconnect()
        }
      },
      { rootMargin: "600px 0px" },
    )
    observer.observe(el)
    // Filet : certains navigateurs intégrés (WhatsApp, Facebook) ou onglets en arrière-plan ne
    // notifient jamais l'observateur ; l'extrait finit alors par s'afficher quand même, une fois
    // la page installée et le réseau libéré.
    const filet = window.setTimeout(() => setProche(true), 8000)
    return () => {
      observer.disconnect()
      window.clearTimeout(filet)
    }
  }, [proche])

  if (!proche) {
    return (
      <div ref={repere} aria-hidden="true" className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    )
  }

  return (
    <Suspense fallback={<Skeleton className="h-24 w-full" />}>
      <EpreuveMarkdown markdown={markdown} directCoursLinks={directCoursLinks} />
    </Suspense>
  )
}
