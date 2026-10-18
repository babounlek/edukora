import { ArrowLeft, ArrowRight, ArrowUp } from "lucide-react"

import {
  exerciceAnchorId,
  libelleCourtExercice,
  sectionDeLExercice,
  sectionsDEpreuve,
  type ExerciceLabelSource,
} from "@/components/EpreuveSommaire"
import { t, useI18n } from "@/lib/i18n"

interface ExerciceNavProps {
  exercises: ExerciceLabelSource[]
  index: number
}

/**
 * Pied de bloc d'un exercice : "← Ex. 2 · Haut de page · Ex. 4 →". Sans ça, terminer un
 * corrigé et rejoindre le suivant oblige à défiler à l'aveugle jusqu'au prochain
 * séparateur - le sommaire (voir EpreuveSommaire) répond à "où est l'exercice X ?",
 * pas à "et maintenant ?".
 *
 * Les liens sont de simples ancres vers les blocs voisins, la même cible que le
 * sommaire - donc le même comportement de défilement, et une URL partageable.
 *
 * Dans une longue épreuve à sections, le voisin d'une AUTRE section le dit (« Ex. 13 · SECTION 5.5 ») :
 * passer de la dernière question d'une section à la première de la suivante n'est pas anodin quand
 * l'élève ne traite que les questions d'une seule section.
 */
export function ExerciceNav({ exercises, index }: ExerciceNavProps) {
  useI18n()
  const precedent = exercises[index - 1]
  const suivant = exercises[index + 1]
  const sections = sectionsDEpreuve(exercises)
  const courante = sectionDeLExercice(sections, index)
  const etiquette = (voisin: ExerciceLabelSource, rang: number) => {
    const autre = sectionDeLExercice(sections, rang)
    return autre && courante && autre.cle !== courante.cle
      ? `${libelleCourtExercice(voisin)} · ${autre.label}`
      : libelleCourtExercice(voisin)
  }

  return (
    <div className="not-prose mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4 text-sm text-muted-foreground">
      {precedent ? (
        <a
          href={`#${exerciceAnchorId(precedent.numero_exercice)}`}
          className="inline-flex min-h-11 items-center gap-1.5 px-1 transition-colors hover:text-primary"
        >
          <ArrowLeft className="size-4" />
          {etiquette(precedent, index - 1)}
        </a>
      ) : (
        // Placeholder : garde "suivant" aligné à droite sur le premier exercice.
        <span />
      )}

      <button
        type="button"
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        className="inline-flex min-h-11 items-center gap-1.5 px-1 transition-colors hover:text-primary"
      >
        <ArrowUp className="size-4" />
        {t("ed.haut_de_page")}
      </button>

      {suivant ? (
        <a
          href={`#${exerciceAnchorId(suivant.numero_exercice)}`}
          className="inline-flex min-h-11 items-center gap-1.5 px-1 font-medium text-primary transition-colors hover:underline"
        >
          {etiquette(suivant, index + 1)}
          <ArrowRight className="size-4" />
        </a>
      ) : (
        <span />
      )}
    </div>
  )
}
