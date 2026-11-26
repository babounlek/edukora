import { Link } from "react-router-dom"
import { ArrowRight, Layers } from "lucide-react"

import { trackEvent } from "@/lib/analytics"
import { useCursusDeclare } from "@/lib/cursusAccueil"
import { useFicheDUnTheme, useFichesDeLExamen } from "@/lib/useFichesDeLExamen"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * L'examen dont proposer les fiches sous un contenu : celui que l'élève prépare s'il fait partie des examens du contenu ;
 * sans examen déclaré, le premier du contenu. Aucun si l'élève prépare un autre examen. La plupart des cours ne sont
 * rattachés à aucun examen : ceux-là suivent l'examen déclaré.
 */
export function useCursusDesFiches(examensDuContenu: { id: number }[] | undefined): number | null {
  const declare = useCursusDeclare()
  if (!examensDuContenu) return null
  if (examensDuContenu.length === 0) return declare
  if (declare === null) return examensDuContenu[0].id
  return examensDuContenu.some((c) => c.id === declare) ? declare : null
}

/**
 * La porte vers les Fiches EduKora : sur l'accueil (toutes celles de l'examen) et sous un cours, un corrigé ou un résultat
 * de quiz (celles de la matière : la plupart des fiches ne portent pas de thème). `matiereCode` absent = tout l'examen ;
 * null = matière inconnue, rien. Sans fiche publiée, rien n'est affiché.
 */
export function LienFiches({
  cursusId, matiereCode, source, themes, className,
}: {
  cursusId: number | null | undefined
  /** D'où part le clic, pour la mesure. */
  source: "accueil" | "cours" | "corrige" | "quiz"
  matiereCode?: string | null
  /** Les thèmes à retravailler, le plus fragile d'abord : le lien ouvre alors la fiche de l'un d'eux, s'il y en a une. */
  themes?: number[]
  className?: string
}) {
  useI18n()
  const { matieres, total, noms } = useFichesDeLExamen(cursusId)
  const matiere = matiereCode ? matieres.find((m) => m.matiere_code === matiereCode) : undefined
  const fiche = useFicheDUnTheme(cursusId, matiere?.matiere_id, themes ?? [])
  if (matiereCode === undefined ? total === 0 : !matiere) return null
  const cible = `/fiches-edukora?cursus=${cursusId}${matiere ? `&matiere=${matiere.matiere_id}` : ""}${fiche ? `&fiche=${fiche.id}` : ""}`
  return (
    <Link
      to={cible}
      onClick={() => trackEvent("fiche_lien_clic", { source, cursus_id: cursusId, matiere_id: matiere?.matiere_id })}
      className={cn(
        "group flex items-center gap-3 rounded-2xl border border-gold/40 bg-gold/[0.07] px-5 py-4 transition-colors hover:border-gold/70 print:hidden",
        className,
      )}
    >
      <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gold/20 text-gold-text">
        <Layers className="size-5" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block font-display font-semibold">
          {fiche ? t("fl.fiche") : matiere ? tn("fl.matiere", matiere.total, { matiere: matiere.matiere }) : tn("fl.examen", total)}
        </span>
        <span className="block text-sm text-muted-foreground">{fiche ? fiche.terme : matiere ? t("fl.matiere_texte") : noms}</span>
      </span>
      <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
    </Link>
  )
}
