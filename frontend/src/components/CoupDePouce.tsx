import { useState } from "react"
import { Lightbulb } from "lucide-react"

import { getIndiceQuiz } from "@/api/endpoints"
import type { Difficulte } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { Button } from "@/components/ui/button"
import { t, useI18n, type CleI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

const TEINTE: Record<Difficulte, string> = {
  FAIBLE: "border-success/40 bg-success/10 text-success",
  MOYENNE: "border-gold/40 bg-gold/10 text-gold-text",
  ELEVEE: "border-destructive/30 bg-destructive/10 text-destructive",
}

/** La difficulté estimée d'une question (R19) : un mot, pas seulement une couleur. Rien quand elle n'est pas estimée. */
export function PastilleDifficulte({ difficulte }: { difficulte: Difficulte | null | undefined }) {
  useI18n()
  if (!difficulte) return null
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold", TEINTE[difficulte])}>
      {t(`difficulte.${difficulte}` as CleI18n)}
    </span>
  )
}

/**
 * Le coup de pouce (R19) : la méthode, pas la réponse. Un bouton sous l'énoncé qui déplie le « Rappel de méthode » du
 * corrigé ; la clé et les explications ne sortent du serveur qu'après la réponse. Demander un coup de pouce est permis et
 * sans pénalité : mieux vaut qu'il serve que l'élève devine.
 */
export function CoupDePouce({ sessionId, questionId }: { sessionId: number; questionId: number }) {
  useI18n()
  const [indice, setIndice] = useState<string | null>(null)
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState(false)

  async function demander() {
    setChargement(true)
    setErreur(false)
    try {
      setIndice((await getIndiceQuiz(sessionId, questionId)).indice_markdown)
    } catch {
      setErreur(true)
    } finally {
      setChargement(false)
    }
  }

  if (indice !== null) {
    return (
      <div className="mt-5 rounded-xl border border-gold/40 bg-gold/5 px-4 py-3">
        <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-gold-text">
          <Lightbulb className="size-3.5" aria-hidden="true" />
          {t("pouce.titre")}
        </p>
        <article className="prose prose-sm prose-neutral mt-1.5 max-w-none dark:prose-invert">
          <EpreuveMarkdown markdown={indice} />
        </article>
      </div>
    )
  }

  return (
    <div className="mt-5">
      <Button type="button" variant="outline" size="sm" onClick={demander} disabled={chargement}>
        <Lightbulb className="size-4" aria-hidden="true" />
        {t("pouce.bouton")}
      </Button>
      {erreur && (
        <p role="alert" className="mt-2 text-sm text-destructive">
          {t("pouce.erreur")}
        </p>
      )}
    </div>
  )
}
