import { Info, TriangleAlert } from "lucide-react"

import type { RegleChoix } from "@/api/types"
import { t, tn } from "@/lib/i18n"

interface Props {
  regles: RegleChoix[]
  /**
   * Ids des exercices que l'élève a déclarés traités. Fourni : la simulation - l'écran compte les
   * exercices traités et dit que seuls les meilleurs comptent. Absent : le sujet lu en ligne, où
   * rien ne se note, et la consigne reste une simple information.
   */
  traites?: Set<number>
}

/**
 * Consignes de choix d'une épreuve du GCE (« 4 questions sur 5 », « toutes dans une seule section »,
 * « 4 au total, au moins une par section »). Les règles « parmi », « section_unique » et « total » agissent
 * sur la note d'une simulation ; « ou » et « consigne » sont à lire.
 */
export function ReglesChoix({ regles, traites }: Props) {
  if (regles.length === 0) return null
  const simulation = traites !== undefined
  return (
    <ul aria-label={t("ct.consignes_choix_aria")} className="mb-6 flex flex-col gap-2">
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
        if (regle.type === "consigne") {
          return (
            <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
              <Info className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
              {t("ct.regle_consigne", { portee: regle.portee, texte: regle.texte })}
            </li>
          )
        }
        const intitule =
          regle.type === "parmi"
            ? tn(simulation ? "ct.regle_parmi" : "ct.annale_parmi", regle.repondre, { portee: regle.portee, m: regle.sur })
            : regle.type === "total"
              ? tn(simulation ? "ct.regle_total" : "ct.annale_total", regle.repondre, {
                  portee: regle.portee,
                  min: regle.minimum,
                })
              : tn(simulation ? "ct.regle_section_unique" : "ct.annale_section_unique", regle.repondre, {
                  portee: regle.portee,
                })
        if (!simulation) {
          return (
            <li key={i} className="flex items-start gap-2 rounded-xl border border-border bg-muted/40 px-3 py-2 text-sm">
              <Info className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
              {intitule}
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
                {intitule}{" "}
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
