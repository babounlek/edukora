import { useEffect, useRef, useState } from "react"

import type { EpreuveExercise } from "@/api/types"
import { apercuQuestion, exerciceAnchorId, libelleCourtExercice, sectionsDEpreuve } from "@/components/EpreuveSommaire"
import { useFonduDefilement } from "@/components/FiltresCatalogue"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/** Fait défiler la rangée pour que la pastille visée y soit centrée (téléphone). */
function centrer(liste: HTMLElement | null, cible: string | null) {
  if (!liste || !cible) return
  const pastille = liste.querySelector<HTMLElement>(`[data-cible="${cible}"]`)
  if (!pastille) return
  liste.scrollTo({ left: pastille.offsetLeft - liste.clientWidth / 2 + pastille.clientWidth / 2, behavior: "smooth" })
}

const PASTILLE = "inline-flex min-h-9 items-center rounded-full border px-3.5 text-sm font-medium transition-colors"
const PASTILLE_ACTIVE = "border-primary bg-primary text-primary-foreground shadow-sm"
const PASTILLE_REPOS = "border-border text-muted-foreground hover:border-primary/40 hover:text-primary"

/**
 * La barre de navigation d'une épreuve lue en ligne : une pastille par exercice, collée sous
 * l'en-tête du site pendant tout le défilement. L'exercice en cours de lecture y est allumé.
 *
 * C'est la réponse à "où en suis-je, et comment aller à l'exercice 4 sans tout défiler" : le
 * sommaire latéral (voir EpreuveSommaire) rétrécissait la colonne de lecture, et une rangée
 * horizontale marche aussi bien sur téléphone que sur grand écran.
 *
 * Une longue épreuve groupée (voir sectionsDEpreuve : 36 questions réparties en six sections au
 * GCE) passe sur deux rangées - les sections, puis seulement les questions de la section en cours :
 * 36 pastilles à la suite ne se parcourent plus. Les pastilles gardent le numéro imprimé du sujet.
 *
 * L'exercice actif est celui qui traverse une ligne placée à un tiers de la hauteur de l'écran,
 * là où l'œil est posé - pas celui dont le haut vient d'apparaître en bas.
 */
export function BarreExercices({ exercises }: { exercises: EpreuveExercise[] }) {
  useI18n()
  const [actif, setActif] = useState<string | null>(null)
  const listeRef = useRef<HTMLOListElement>(null)
  const sectionsRef = useRef<HTMLOListElement>(null)
  const sections = sectionsDEpreuve(exercises)
  // Rangées qui défilent, barre de défilement masquée : un fondu à droite dit qu'il reste des exercices (ou des sections).
  const fonduListe = useFonduDefilement(listeRef)
  const fonduSections = useFonduDefilement(sectionsRef)

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

  const sectionActive = sections
    ? (sections.find((section) => section.items.some(({ exercise }) => exerciceAnchorId(exercise.numero_exercice) === actif)) ??
      sections[0])
    : null

  // La pastille active reste visible dans la rangée quand elle défile (téléphone) ; la rangée des
  // sections suit aussi la section en cours.
  useEffect(() => {
    centrer(listeRef.current, actif)
  }, [actif, sectionActive?.cle])
  useEffect(() => {
    centrer(sectionsRef.current, sectionActive ? `section-${sectionActive.cle}` : null)
  }, [sectionActive?.cle])

  if (exercises.length < 2) return null

  const barre =
    "sticky top-[72px] z-20 -mx-4 mb-5 mt-5 border-b border-border bg-background/90 px-4 py-2 backdrop-blur sm:-mx-6 sm:px-6"
  const rangee = "flex gap-1.5 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"

  const pastilles = (items: { exercise: EpreuveExercise }[]) =>
    items.map(({ exercise }) => {
      const id = exerciceAnchorId(exercise.numero_exercice)
      const estActif = actif === id
      return (
        <li key={id} data-cible={id} className="shrink-0">
          <a
            href={`#${id}`}
            aria-current={estActif ? "location" : undefined}
            // Longue épreuve à sections : la question EST l'exercice, son début s'affiche au survol.
            title={sections ? apercuQuestion(exercise.enonce_markdown, exercise.titre) || undefined : undefined}
            className={cn(PASTILLE, estActif ? PASTILLE_ACTIVE : PASTILLE_REPOS)}
          >
            {libelleCourtExercice(exercise)}
          </a>
        </li>
      )
    })

  if (sections && sectionActive) {
    return (
      <nav aria-label={t("ed.exercices_aria")} className={cn(barre, "flex flex-col gap-1.5")}>
        <ol ref={sectionsRef} onScroll={fonduSections.onScroll} className={cn(rangee, fonduSections.fondu)}>
          {sections.map((section) => {
            const estCourante = section.cle === sectionActive.cle
            return (
              <li key={section.cle} data-cible={`section-${section.cle}`} className="shrink-0">
                <a
                  href={`#${exerciceAnchorId(section.items[0].exercise.numero_exercice)}`}
                  aria-current={estCourante ? "location" : undefined}
                  title={section.intitule}
                  className={cn(
                    PASTILLE,
                    "max-w-[16rem] gap-2 truncate font-display text-xs uppercase tracking-wide",
                    estCourante ? PASTILLE_ACTIVE : PASTILLE_REPOS,
                  )}
                >
                  <span className="truncate">{section.label}</span>
                </a>
              </li>
            )
          })}
        </ol>
        <ol ref={listeRef} onScroll={fonduListe.onScroll} className={cn(rangee, fonduListe.fondu)}>
          {pastilles(sectionActive.items)}
        </ol>
      </nav>
    )
  }

  return (
    <nav aria-label={t("ed.exercices_aria")} className={barre}>
      <ol ref={listeRef} onScroll={fonduListe.onScroll} className={cn(rangee, fonduListe.fondu)}>
        {pastilles(exercises.map((exercise) => ({ exercise })))}
      </ol>
    </nav>
  )
}
