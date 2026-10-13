import { Link } from "react-router-dom"
import { CheckCircle2, ClipboardCheck } from "lucide-react"

import type { NotationResume } from "@/api/types"
import { Button } from "@/components/ui/button"
import { formatNote } from "@/lib/notation"
import { tu, type Unite } from "@/lib/vocabulaire"
import { t, useI18n } from "@/lib/i18n"

interface BandeauNotationProps {
  notation: NotationResume
  tentativeId: number
  // Le chrono a rendu l'épreuve à la place de l'élève : on le lui dit, il n'a pas cliqué.
  rendueAutomatiquement: boolean
  onProchaine: () => void
  unite?: Unite
}

/** Sous la barre d'actions, une fois l'épreuve rendue : guide l'élève de « corrigé ouvert »
 * jusqu'à « note définitive ». La notation est la dernière étape, pas un bonus - sans ce
 * bandeau, un élève qui rend sa copie ne saurait pas qu'une note l'attend. */
export function BandeauNotation({
  notation, tentativeId, rendueAutomatiquement, onProchaine, unite = "question", resultatPath,
}: BandeauNotationProps & { resultatPath?: string }) {
  useI18n()
  const traitees = notation.questions_traitees
  const notees = traitees - notation.questions_a_noter
  const introduction = rendueAutomatiquement ? t("bn.intro_rendue") : ""

  if (notation.questions_a_noter === 0) {
    return (
      <div role="status" className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-success/40 bg-success/10 px-4 py-3">
        <p className="flex items-center gap-2 text-sm">
          <CheckCircle2 className="size-5 shrink-0 text-success" />
          <span>
            {introduction}
            {traitees === 0
              ? tu("bn.aucun", unite)
              : t("bn.terminee")}{" "}
            <strong className="tabular-nums">{formatNote(notation.note, notation.bareme)}</strong>
          </span>
        </p>
        <Button asChild size="sm">
          <Link to={resultatPath ?? `/inedit/tentative/${tentativeId}/resultat`}>{t("qs.voir_resultat")}</Link>
        </Button>
      </div>
    )
  }

  return (
    <div role="status" className="mb-6 rounded-xl border border-primary/30 bg-primary/5 px-4 py-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="flex items-start gap-2 text-sm">
          <ClipboardCheck className="mt-0.5 size-5 shrink-0 text-primary" />
          <span>
            {introduction}
            <strong>{t("bn.corrige_ouvert")}</strong>{" "}
            {traitees === 1 ? tu("bn.une", unite) : tu("bn.plusieurs", unite, { n: traitees })}
          </span>
        </p>
        <Button size="sm" onClick={onProchaine}>
          {tu("bn.suivante", unite)}
        </Button>
      </div>
      <div className="mt-3 flex items-center gap-2.5">
        <div
          role="progressbar"
          aria-label={tu("bn.label", unite)}
          aria-valuemin={0}
          aria-valuemax={traitees}
          aria-valuenow={notees}
          className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary"
        >
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${traitees ? (notees / traitees) * 100 : 0}%` }}
          />
        </div>
        <span className="shrink-0 text-xs font-medium tabular-nums text-muted-foreground">
          {t("bn.compte", { n: notees, total: traitees })}
        </span>
      </div>
    </div>
  )
}
