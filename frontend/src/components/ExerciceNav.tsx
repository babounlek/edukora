import { ArrowLeft, ArrowRight, ArrowUp } from "lucide-react"

import { exerciceAnchorId, libelleCourtExercice, type ExerciceLabelSource } from "@/components/EpreuveSommaire"

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
 */
export function ExerciceNav({ exercises, index }: ExerciceNavProps) {
  const precedent = exercises[index - 1]
  const suivant = exercises[index + 1]

  return (
    <div className="not-prose mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4 text-sm text-muted-foreground">
      {precedent ? (
        <a
          href={`#${exerciceAnchorId(precedent.numero_exercice)}`}
          className="inline-flex items-center gap-1.5 transition-colors hover:text-primary"
        >
          <ArrowLeft className="size-4" />
          {libelleCourtExercice(precedent)}
        </a>
      ) : (
        // Placeholder : garde "suivant" aligné à droite sur le premier exercice.
        <span />
      )}

      <button
        type="button"
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        className="inline-flex items-center gap-1.5 transition-colors hover:text-primary"
      >
        <ArrowUp className="size-4" />
        Haut de page
      </button>

      {suivant ? (
        <a
          href={`#${exerciceAnchorId(suivant.numero_exercice)}`}
          className="inline-flex items-center gap-1.5 font-medium text-primary transition-colors hover:underline"
        >
          {libelleCourtExercice(suivant)}
          <ArrowRight className="size-4" />
        </a>
      ) : (
        <span />
      )}
    </div>
  )
}
