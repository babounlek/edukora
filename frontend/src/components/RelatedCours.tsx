import { useEffect, useState } from "react"

import { listCours } from "@/api/endpoints"
import type { Cours } from "@/api/types"
import { CoursCard } from "@/components/CoursCard"

interface RelatedCoursProps {
  subjectCode: string
  subjectLabel: string
  countryCode: string
  cursusId?: number
  excludeId: number
  // Sous-thème du cours consulté (voir catalog.Cours.sous_theme) - les cours qui le
  // partagent remontent en tête des suggestions plutôt que de se retrouver noyés dans
  // le reste de la matière (voir CoursListView.sous_theme_prioritaire côté backend).
  sousTheme?: string
}

/** Même patron que RelatedEpreuves - même matière + même série que le cours consulté, en écartant ce qui a déjà été lu. */
export function RelatedCours({ subjectCode, subjectLabel, countryCode, cursusId, excludeId, sousTheme }: RelatedCoursProps) {
  const [relatedCours, setRelatedCours] = useState<Cours[]>([])

  useEffect(() => {
    listCours({
      ...(cursusId ? { subject: subjectCode, cursus: cursusId } : { subject: subjectCode, country: countryCode }),
      exclude_read: true,
      ...(sousTheme ? { sous_theme_prioritaire: sousTheme } : {}),
    })
      .then((data) => {
        setRelatedCours(data.results.filter((c) => c.id !== excludeId).slice(0, 4))
      })
      .catch(() => {})
  }, [subjectCode, countryCode, cursusId, excludeId, sousTheme])

  if (relatedCours.length === 0) return null

  return (
    <div className="mt-2 border-t border-border pt-5">
      <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">
        Autres cours de {subjectLabel}
      </h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {relatedCours.map((c) => (
          <CoursCard key={c.id} cours={c} />
        ))}
      </div>
    </div>
  )
}
