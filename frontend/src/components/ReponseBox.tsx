import type { ReactNode } from "react"
import { CheckCircle2 } from "lucide-react"

import { t, useI18n } from "@/lib/i18n"

interface ReponseBoxProps {
  children?: ReactNode
}

/**
 * La réponse finale d'un corrigé (« Answer: B. », conclusion chiffrée d'un calcul), dans un encadré vert qui la
 * sort du texte d'explication. Même habillage que <Callout> : le `not-prose` ne va que sur l'étiquette, jamais sur
 * le conteneur, sans quoi la typographie de la réponse (formules, gras) serait coupée pour tout le sous-arbre.
 */
export function ReponseBox({ children }: ReponseBoxProps) {
  useI18n()

  return (
    <div
      role="note"
      className="my-5 rounded-lg border border-success/40 border-l-4 border-l-success bg-success/10 px-4 py-3 text-foreground"
    >
      <p className="not-prose mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-success">
        <CheckCircle2 className="size-4 shrink-0" aria-hidden="true" />
        {t("gl.reponse_finale")}
      </p>
      <div className="prose prose-neutral max-w-none text-base font-semibold dark:prose-invert prose-p:my-0 prose-strong:text-foreground">
        {children}
      </div>
    </div>
  )
}
