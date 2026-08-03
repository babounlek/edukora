import { useEffect, useState } from "react"

import { listEpreuves } from "@/api/endpoints"
import type { Epreuve } from "@/api/types"
import { EpreuveCard } from "@/components/EpreuveCard"

interface RelatedEpreuvesProps {
  subjectCode: string
  subjectLabel: string
  countryCode: string
  cursusId?: number
  excludeId: number
}

export function RelatedEpreuves({ subjectCode, subjectLabel, countryCode, cursusId, excludeId }: RelatedEpreuvesProps) {
  const [relatedEpreuves, setRelatedEpreuves] = useState<Epreuve[]>([])

  useEffect(() => {
    // Même matière + même série (cursus) que l'épreuve consultée : un élève de Série C
    // ne se soucie pas d'un sujet Série D de la même matière. La récence (via le tri
    // par défaut -year du Lesson) ne joue qu'en critère secondaire, une fois la liste
    // déjà restreinte à ce qui est pertinent pour son cursus. exclude_read écarte ce
    // qui a déjà été lu pour ne pousser que du contenu neuf - no-op côté backend pour
    // un visiteur anonyme (voir LessonListView.get_queryset), donc pas de branchement
    // ici selon l'état de connexion.
    listEpreuves(
      cursusId
        ? { subject: subjectCode, cursus: cursusId, exclude_read: true }
        : { subject: subjectCode, country: countryCode, exclude_read: true },
    )
      .then((data) => {
        setRelatedEpreuves(data.results.filter((e) => e.id !== excludeId).slice(0, 4))
      })
      .catch(() => {})
  }, [subjectCode, countryCode, cursusId, excludeId])

  if (relatedEpreuves.length === 0) return null

  return (
    <div className="mt-2 border-t border-border pt-5">
      <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">
        Autres épreuves de {subjectLabel}
      </h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {relatedEpreuves.map((e) => (
          <EpreuveCard key={e.id} epreuve={e} />
        ))}
      </div>
    </div>
  )
}
