import { useState } from "react"
import { NotebookPen } from "lucide-react"

import { AjouterNoteDialog } from "@/components/AjouterNoteDialog"
import { Button } from "@/components/ui/button"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Ajouter à mes notes » sous la correction d'une question de quiz : une erreur devient une note, rangée dans le dossier de
 * sa matière, avec la question en citation. Rien ne s'affiche quand la matière n'est pas connue (anciennes séances).
 */
export function AjouterAMesNotes({ subjectId, enonce }: { subjectId?: number | null; enonce: string }) {
  useI18n()
  const [ouvert, setOuvert] = useState(false)
  if (!subjectId) return null
  return (
    <>
      <Button type="button" variant="ghost" size="sm" className="mt-3 rounded-full text-muted-foreground" onClick={() => setOuvert(true)}>
        <NotebookPen className="size-4" />
        {t("ca.ajouter_a_mes_notes")}
      </Button>
      <AjouterNoteDialog open={ouvert} onOpenChange={setOuvert} subjectId={subjectId} citation={enonce.replace(/\s+/g, " ").trim()} />
    </>
  )
}
