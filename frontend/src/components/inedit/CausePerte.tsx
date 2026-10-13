import { cn } from "@/lib/utils"
import { t, useI18n, type CleI18n } from "@/lib/i18n"

export type CauseCode = "TEMPS" | "CONNAISSANCE" | "METHODE" | "CALCUL" | "INATTENTION"

const CAUSES: { code: CauseCode; label: CleI18n }[] = [
  { code: "CONNAISSANCE", label: "cp.connaissance" },
  { code: "METHODE", label: "cp.methode" },
  { code: "CALCUL", label: "cp.calcul" },
  { code: "INATTENTION", label: "cp.inattention" },
  { code: "TEMPS", label: "cp.temps" },
]

// Une question laissée de côté ne relève que de deux causes : le temps, ou la notion.
const CAUSES_NON_TRAITEE = CAUSES.filter((c) => c.code === "TEMPS" || c.code === "CONNAISSANCE")

interface CausePerteProps {
  valeur: string
  // Question non traitée : moins de choix, une autre formulation.
  nonTraitee?: boolean
  onChoisir: (cause: CauseCode | "") => void
}

/**
 * « Pourquoi as-tu perdu des points ici ? » - facultatif, deux clics au plus. Chaque réponse
 * nourrit le rapport de fin d'épreuve (voir InediteResultPage) : savoir qu'on perd ses points
 * par erreurs de calcul plutôt que par ignorance change ce qu'on révise. Cliquer sur la cause
 * déjà choisie l'efface : on ne reste jamais coincé sur un clic malheureux.
 */
export function CausePerte({ valeur, nonTraitee, onChoisir }: CausePerteProps) {
  useI18n()
  const choix = nonTraitee ? CAUSES_NON_TRAITEE : CAUSES
  return (
    <fieldset className="rounded-xl border border-dashed border-border px-3 py-2.5">
      <legend className="px-1 text-xs font-medium text-muted-foreground">
        {nonTraitee ? t("cp.pourquoi_non_traitee") : t("cp.pourquoi_perdu")}
      </legend>
      <div className="flex flex-wrap gap-1.5">
        {choix.map(({ code, label }) => (
          <button
            key={code}
            type="button"
            aria-pressed={valeur === code}
            onClick={() => onChoisir(valeur === code ? "" : code)}
            className={cn(
              "min-h-9 rounded-full border px-3 text-sm transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
              valeur === code ? "border-primary bg-primary/10 font-medium" : "border-border hover:bg-accent/40",
            )}
          >
            {t(label)}
          </button>
        ))}
      </div>
    </fieldset>
  )
}
