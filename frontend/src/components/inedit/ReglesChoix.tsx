import { Info, TriangleAlert } from "lucide-react"

import type { RegleChoix } from "@/api/types"
import { t, tn } from "@/lib/i18n"

interface Props {
  regles: RegleChoix[]
  /** Ids des exercices que l'élève a déclarés traités. */
  traites: Set<number>
}

/**
 * Consignes de choix d'une épreuve du GCE (« 4 questions sur 5 »). Seules les règles « parmi »
 * agissent sur la note ; les règles « ou » sont une consigne à lire.
 */
export function ReglesChoix({ regles, traites }: Props) {
  if (regles.length === 0) return null
  return (
    <ul className="mb-6 flex flex-col gap-2">
      {regles.map((regle, i) => {
        if (regle.type === "ou") {
          const options = regle.options.map((jeu) => jeu.join(", ")).join(` ${t("ct.ou")} `)
          return (
            <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
              <Info className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
              {t("ct.regle_ou", { portee: regle.portee, options })}
            </li>
          )
        }
        const fait = (regle.exercices ?? []).filter((id) => traites.has(id)).length
        const trop = fait > regle.repondre
        return (
          <li key={i} className="rounded-xl border border-border bg-muted/40 px-3 py-2 text-sm">
            <p className="flex items-start gap-2">
              <Info className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
              <span>
                {tn("ct.regle_parmi", regle.repondre, { portee: regle.portee, m: regle.sur })}{" "}
                <span className="tabular-nums text-muted-foreground">
                  {t("ct.regle_parmi_etat", { fait, n: regle.repondre })}
                </span>
              </span>
            </p>
            {trop && (
              <p role="status" className="mt-1 flex items-start gap-2 text-amber-700 dark:text-amber-400">
                <TriangleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
                {t("ct.regle_parmi_trop", { n: regle.repondre })}
              </p>
            )}
          </li>
        )
      })}
    </ul>
  )
}
