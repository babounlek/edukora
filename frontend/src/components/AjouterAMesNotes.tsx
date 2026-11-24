import { useState } from "react"
import { NotebookPen } from "lucide-react"

import type { QuizChoix } from "@/api/types"
import { AjouterNoteDialog } from "@/components/AjouterNoteDialog"
import { Button } from "@/components/ui/button"
import { t, useI18n } from "@/lib/i18n"

/** « B : x² » : la bonne réponse d'un QCM, telle qu'on l'écrirait dans sa note (rien si elle n'est pas connue). */
export function bonneReponseEnNote(choix: QuizChoix[], lettre?: string): string | undefined {
  if (!lettre) return undefined
  const juste = choix.find((c) => c.lettre === lettre)
  return juste ? `${lettre.toUpperCase()} : ${juste.texte}` : lettre.toUpperCase()
}

/**
 * « Noter cette erreur » sous la correction d'une question de quiz : une erreur devient une note, rangée dans le dossier de
 * sa matière, avec la question en citation et la bonne réponse déjà écrite. Après une erreur le bouton est bien visible
 * (c'est là qu'une note sert le plus) ; après une bonne réponse il reste discret. Rien ne s'affiche quand la matière n'est
 * pas connue (anciennes séances).
 */
export function AjouterAMesNotes({
  subjectId, enonce, erreur = false, bonneReponse, source,
}: { subjectId?: number | null; enonce: string; erreur?: boolean; bonneReponse?: string; source?: string }) {
  useI18n()
  const [ouvert, setOuvert] = useState(false)
  if (!subjectId) return null
  return (
    <>
      <Button
        type="button"
        variant={erreur ? "outline" : "ghost"}
        size="sm"
        className={erreur ? "mt-4 rounded-full border-primary/40 text-primary" : "mt-3 rounded-full text-muted-foreground"}
        onClick={() => setOuvert(true)}
      >
        <NotebookPen className="size-4" />
        {t(erreur ? "ca.noter_erreur_bouton" : "ca.ajouter_a_mes_notes")}
      </Button>
      <AjouterNoteDialog
        open={ouvert}
        onOpenChange={setOuvert}
        subjectId={subjectId}
        joignables={{ question: enonce.replace(/\s+/g, " ").trim(), bonneReponse }}
        joindreParDefaut={erreur}
        origine="quiz"
        source={source}
      />
    </>
  )
}
