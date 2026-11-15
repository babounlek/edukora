import { useState } from "react"
import { Check, Flag } from "lucide-react"

import { signalerQuestionQuiz } from "@/api/endpoints"
import type { MotifSignalement } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { t, useI18n, type CleI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

const MOTIFS: MotifSignalement[] = ["REPONSE_FAUSSE", "ENONCE_CONFUS", "FIGURE", "HORS_PROGRAMME", "AUTRE"]

/**
 * « Signaler cette question » (audit produit 2026-11-13, R22) : un lien discret sous la question, une boîte avec un motif et
 * un mot facultatif. Ni points ni maîtrise n'en dépendent : l'élève dit ce qui cloche, l'équipe corrige. Une fois envoyé, le
 * lien devient « Merci, signalé » pour cette question.
 */
export function SignalerQuestion({ sessionId, questionId }: { sessionId: number; questionId: number }) {
  useI18n()
  const [ouvert, setOuvert] = useState(false)
  const [motif, setMotif] = useState<MotifSignalement | null>(null)
  const [commentaire, setCommentaire] = useState("")
  const [envoi, setEnvoi] = useState(false)
  const [erreur, setErreur] = useState("")
  const [signale, setSignale] = useState<number | null>(null)

  async function envoyer() {
    if (!motif || envoi) return
    setEnvoi(true)
    setErreur("")
    try {
      await signalerQuestionQuiz(sessionId, questionId, { motif, commentaire: commentaire.trim() })
      setSignale(questionId)
      setOuvert(false)
      setMotif(null)
      setCommentaire("")
    } catch {
      setErreur(t("signaler.erreur"))
    } finally {
      setEnvoi(false)
    }
  }

  if (signale === questionId) {
    return (
      <p className="mt-4 flex items-center gap-1.5 text-xs text-muted-foreground" role="status">
        <Check className="size-3.5 text-success" aria-hidden="true" />
        {t("signaler.merci")}
      </p>
    )
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOuvert(true)}
        className="mt-4 inline-flex items-center gap-1.5 text-xs text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
      >
        <Flag className="size-3.5" aria-hidden="true" />
        {t("signaler.lien")}
      </button>
      <Dialog open={ouvert} onOpenChange={setOuvert}>
        <DialogContent className="sm:max-w-md">
          <DialogTitle>{t("signaler.titre")}</DialogTitle>
          <DialogDescription>{t("signaler.texte")}</DialogDescription>
          <div role="radiogroup" aria-label={t("signaler.titre")} className="mt-2 flex flex-col gap-2">
            {MOTIFS.map((m) => (
              <button
                key={m}
                type="button"
                role="radio"
                aria-checked={motif === m}
                onClick={() => setMotif(m)}
                className={cn(
                  "rounded-xl border px-3 py-2.5 text-left text-sm transition-colors",
                  motif === m ? "border-primary bg-primary/10 font-medium" : "border-border hover:bg-accent/40",
                )}
              >
                {t(`signaler.motif_${m}` as CleI18n)}
              </button>
            ))}
          </div>
          <textarea
            value={commentaire}
            onChange={(e) => setCommentaire(e.target.value)}
            maxLength={500}
            rows={3}
            placeholder={t("signaler.precision")}
            aria-label={t("signaler.precision")}
            className="mt-2 w-full rounded-xl border border-border bg-background px-3 py-2 text-sm"
          />
          {erreur && (
            <p role="alert" className="text-sm text-destructive">
              {erreur}
            </p>
          )}
          <Button onClick={envoyer} disabled={!motif || envoi} className="mt-2 w-full">
            {t("signaler.envoyer")}
          </Button>
        </DialogContent>
      </Dialog>
    </>
  )
}
