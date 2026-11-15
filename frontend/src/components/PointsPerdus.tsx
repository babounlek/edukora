import { useQuery } from "@tanstack/react-query"
import { Target } from "lucide-react"

import { getMesPertes } from "@/api/endpoints"
import { t, tn, useI18n } from "@/lib/i18n"

/** Sans cause déclarée, un camembert ne dirait rien : le message ne parle que d'une cause que l'élève a nommée. */
const CAUSES_NON_DECLAREES = ["NON_PRECISEE"]

/**
 * « Où partent tes points » (audit produit 2026-11-13, R23) : le cumul des causes de perte déclarées après le corrigé, sur les
 * dernières copies rendues. Une panne ou l'absence de copie ne montre rien : c'est un plus, pas une page à part.
 */
export function PointsPerdus() {
  useI18n()
  const { data } = useQuery({ queryKey: ["mes-pertes"], queryFn: ({ signal }) => getMesPertes(signal) })
  if (!data || data.copies === 0 || data.causes.length === 0) return null

  const [premiere] = data.causes
  const nommee = !CAUSES_NON_DECLAREES.includes(premiere.cause)

  return (
    <section aria-labelledby="pertes-titre" className="mt-4 rounded-2xl border border-border bg-card p-4">
      <h2 id="pertes-titre" className="flex items-center gap-1.5 font-display text-base font-semibold">
        <Target className="size-4 text-primary" aria-hidden="true" />
        {t("pertes.titre")}
      </h2>
      <p className="mt-1 text-sm text-muted-foreground">
        {nommee
          ? t("pertes.surtout", { cause: premiere.libelle.toLowerCase(), part: premiere.part })
          : t("pertes.preciser")}
      </p>
      <ul className="mt-3 flex flex-col gap-2">
        {data.causes.map((c) => (
          <li key={c.cause}>
            <div className="flex items-baseline justify-between gap-3 text-sm">
              <span>{c.libelle}</span>
              <span className="tabular-nums text-muted-foreground">{c.part} %</span>
            </div>
            <span className="mt-1 block h-1.5 overflow-hidden rounded-full bg-muted" aria-hidden="true">
              <span className="block h-full rounded-full bg-primary/70" style={{ width: `${Math.max(c.part, 3)}%` }} />
            </span>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-xs text-muted-foreground">{tn("pertes.sur_copies", data.copies)}</p>
    </section>
  )
}
