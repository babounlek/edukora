import { ArrowUpRight, Brain, Pin } from "lucide-react"

import type { CarnetDossier } from "@/api/types"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/** L'aperçu d'un dossier : sa note la plus récente, en clair (ni signes Markdown ni « $ » de formule). */
function enClair(texte: string): string {
  return texte.replace(/\*\*|\$|^[-#>]\s*/gm, "").replace(/\s+/g, " ").trim()
}

/**
 * Un dossier de Mes notes : une chemise à onglet, à la couleur et au pictogramme de sa matière (les mêmes que partout
 * ailleurs dans l'application : on reconnaît « les maths » sans lire). L'onglet dépasse en haut, comme sur une vraie
 * chemise ; la dernière note écrite se lit dessous, pour que le dossier ne soit pas une boîte fermée.
 */
export function CarteDossier({ dossier, onOuvrir, rang = 0 }: { dossier: CarnetDossier; onOuvrir: () => void; rang?: number }) {
  useI18n()
  const couleur = couleurMatiere(dossier.matiere_code)
  const Icone = subjectIcon(dossier.matiere_code ?? "")
  const apercu = enClair(dossier.apercu ?? "")
  return (
    <button
      type="button"
      onClick={onOuvrir}
      style={{ animationDelay: `${Math.min(rang, 8) * 45}ms` }}
      className="group relative block h-full w-full animate-fade-up pt-3 text-left outline-none"
    >
      {/* L'onglet de la chemise. */}
      <span aria-hidden="true" className={cn("absolute left-5 top-0 h-4 w-20 rounded-t-lg opacity-80", couleur.barre)} />
      <span className="relative flex h-full flex-col rounded-2xl border border-border bg-card p-4 shadow-sm transition-all duration-300 group-hover:-translate-y-1 group-hover:border-primary/30 group-hover:shadow-xl group-hover:shadow-primary/10 group-focus-visible:ring-2 group-focus-visible:ring-ring sm:p-5">
        <span className="flex items-start gap-3">
          <span className={cn("flex size-11 shrink-0 items-center justify-center rounded-xl", couleur.puce)}>
            <Icone className="size-5" aria-hidden="true" />
          </span>
          <span className="min-w-0 flex-1">
            <span className="block font-display text-lg font-semibold leading-tight tracking-tight">{dossier.matiere}</span>
            <span className="mt-0.5 block text-xs text-muted-foreground">
              {t(dossier.total === 1 ? "ca.compteur_un" : "ca.compteur_n", { n: dossier.total })}
            </span>
          </span>
          <ArrowUpRight
            className="size-4 shrink-0 text-muted-foreground/50 transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-primary"
            aria-hidden="true"
          />
        </span>
        {apercu && (
          <span className="mt-3 line-clamp-2 border-l-2 border-border pl-3 text-sm leading-snug text-muted-foreground">{apercu}</span>
        )}
        {(dossier.a_reviser > 0 || dossier.epingles > 0) && (
          <span className="mt-auto flex flex-wrap gap-1.5 pt-3">
            {dossier.a_reviser > 0 && (
              <span className="inline-flex items-center gap-1 rounded-full bg-primary px-2.5 py-0.5 text-xs font-medium text-primary-foreground">
                <Brain className="size-3" aria-hidden="true" />
                {t("ca.dossier_a_reviser", { n: dossier.a_reviser })}
              </span>
            )}
            {dossier.epingles > 0 && (
              <span className="inline-flex items-center gap-1 rounded-full bg-gold/15 px-2.5 py-0.5 text-xs font-medium text-gold-text">
                <Pin className="size-3 fill-current" aria-hidden="true" />
                {dossier.epingles}
              </span>
            )}
          </span>
        )}
      </span>
    </button>
  )
}
