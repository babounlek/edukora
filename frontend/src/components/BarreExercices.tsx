import { useEffect, useRef, useState } from "react"

import type { EpreuveExercise } from "@/api/types"
import { exerciceAnchorId, libelleCourtExercice } from "@/components/EpreuveSommaire"
import { cn } from "@/lib/utils"

/**
 * La barre de navigation d'une épreuve lue en ligne : une pastille par exercice, collée sous
 * l'en-tête du site pendant tout le défilement. L'exercice en cours de lecture y est allumé.
 *
 * C'est la réponse à "où en suis-je, et comment aller à l'exercice 4 sans tout défiler" : le
 * sommaire latéral (voir EpreuveSommaire) rétrécissait la colonne de lecture, et une rangée
 * horizontale marche aussi bien sur téléphone que sur grand écran.
 *
 * L'exercice actif est celui qui traverse une ligne placée à un tiers de la hauteur de l'écran,
 * là où l'œil est posé - pas celui dont le haut vient d'apparaître en bas.
 */
export function BarreExercices({ exercises }: { exercises: EpreuveExercise[] }) {
  const [actif, setActif] = useState<string | null>(null)
  const listeRef = useRef<HTMLOListElement>(null)

  useEffect(() => {
    if (exercises.length < 2) return
    const observateur = new IntersectionObserver(
      (entrees) => {
        for (const entree of entrees) if (entree.isIntersecting) setActif(entree.target.id)
      },
      { rootMargin: "-30% 0px -65% 0px" },
    )
    for (const exercise of exercises) {
      const element = document.getElementById(exerciceAnchorId(exercise.numero_exercice))
      if (element) observateur.observe(element)
    }
    return () => observateur.disconnect()
  }, [exercises])

  // La pastille active reste visible dans la rangée quand elle défile (téléphone).
  useEffect(() => {
    const liste = listeRef.current
    if (!liste || !actif) return
    const pastille = liste.querySelector<HTMLElement>(`[data-cible="${actif}"]`)
    if (!pastille) return
    liste.scrollTo({ left: pastille.offsetLeft - liste.clientWidth / 2 + pastille.clientWidth / 2, behavior: "smooth" })
  }, [actif])

  if (exercises.length < 2) return null

  return (
    <nav
      aria-label="Exercices de l'épreuve"
      className="sticky top-[72px] z-20 -mx-4 mb-5 mt-5 border-b border-border bg-background/90 px-4 py-2 backdrop-blur sm:-mx-6 sm:px-6"
    >
      <ol ref={listeRef} className="flex gap-1.5 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {exercises.map((exercise) => {
          const id = exerciceAnchorId(exercise.numero_exercice)
          const estActif = actif === id
          return (
            <li key={id} data-cible={id} className="shrink-0">
              <a
                href={`#${id}`}
                aria-current={estActif ? "location" : undefined}
                className={cn(
                  "inline-flex min-h-9 items-center rounded-full border px-3.5 text-sm font-medium transition-colors",
                  estActif
                    ? "border-primary bg-primary text-primary-foreground shadow-sm"
                    : "border-border text-muted-foreground hover:border-primary/40 hover:text-primary",
                )}
              >
                {libelleCourtExercice(exercise)}
              </a>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
