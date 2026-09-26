import type { ReactNode } from "react"
import { Clock, FileText, Sparkles, type LucideIcon } from "lucide-react"

import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { cn } from "@/lib/utils"

export interface FaitEpreuve {
  icone: LucideIcon
  texte: string
}

/** Les faits d'une épreuve à afficher en une ligne : exercices, durée, coefficient. Le coefficient est
 * un texte libre : on ne l'affiche que quand c'est un nombre simple ("4", "1,5"), jamais une valeur
 * composite ("C,D : 1,5 ; E : 2") qui déborderait. */
export function faitsEpreuve({
  exercices, duree, coefficient,
}: { exercices?: number; duree?: string | null; coefficient?: string | null }): FaitEpreuve[] {
  const faits: FaitEpreuve[] = []
  if (exercices && exercices > 0) faits.push({ icone: FileText, texte: `${exercices} exercice${exercices > 1 ? "s" : ""}` })
  if (duree) faits.push({ icone: Clock, texte: duree })
  if (coefficient && /^\d+([.,]\d+)?$/.test(coefficient.trim())) {
    faits.push({ icone: Sparkles, texte: `Coefficient ${coefficient.trim()}` })
  }
  return faits
}

interface EnTeteEpreuveProps {
  titre: string
  /** Code de la matière (couleur + icône) ; absent tant que l'épreuve n'est pas chargée. */
  matiereCode?: string
  matiere: string
  /** "BAC C et D", "Série D" - le public visé. */
  cursus?: string
  session?: string | number | null
  badges?: ReactNode
  faits?: FaitEpreuve[]
  /** "detail" : grand titre et filigrane ; "lecture" : compact, le corrigé doit rester au premier plan. */
  variante?: "detail" | "lecture"
  /** Actions sous l'en-tête (télécharger, lire le corrigé...). */
  children?: ReactNode
}

/**
 * L'en-tête d'une épreuve, partagé par sa fiche et son lecteur : la matière y est reconnaissable
 * (filet, pastille et filigrane à sa couleur), le titre est au centre, et les faits qui aident à
 * décider - nombre d'exercices, durée, coefficient - tiennent sur une ligne.
 *
 * La couleur est un repère d'identité de matière (voir matiereCouleur), jamais un statut.
 */
export function EnTeteEpreuve({
  titre, matiereCode, matiere, cursus, session, badges, faits = [], variante = "detail", children,
}: EnTeteEpreuveProps) {
  const Icone = subjectIcon(matiereCode ?? "")
  const couleur = couleurMatiere(matiereCode)
  const grand = variante === "detail"

  return (
    <header className="relative overflow-hidden rounded-3xl border border-border bg-card shadow-lg shadow-primary/[0.05]">
      <div aria-hidden className={cn("h-1.5 w-full", couleur.barre)} />
      {grand && (
        <Icone
          aria-hidden
          className={cn("pointer-events-none absolute -bottom-8 -right-6 hidden size-48 rotate-[-10deg] opacity-[0.07] sm:block", couleur.puce.split(" ").filter((c) => c.startsWith("text-")).join(" "))}
        />
      )}
      <div className={cn("relative", grand ? "p-5 sm:p-8" : "p-4 sm:p-6")}>
        <div className="flex items-start gap-4">
          <span
            className={cn(
              "flex shrink-0 items-center justify-center rounded-2xl",
              couleur.puce,
              grand ? "size-14 sm:size-16" : "size-11",
            )}
          >
            <Icone className={grand ? "size-7 sm:size-8" : "size-5"} aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              {matiere}
              {cursus && ` · ${cursus}`}
              {session ? ` · Session ${session}` : ""}
            </p>
            <h1
              className={cn(
                "mt-1 font-display font-semibold leading-tight tracking-tight text-balance",
                grand ? "text-2xl sm:text-4xl" : "text-xl sm:text-2xl",
              )}
            >
              {titre}
            </h1>
          </div>
        </div>

        {badges && <div className="mt-4 flex flex-wrap items-center gap-1.5">{badges}</div>}

        {faits.length > 0 && (
          <ul className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted-foreground">
            {faits.map(({ icone: IconeFait, texte }) => (
              <li key={texte} className="inline-flex items-center gap-1.5">
                <IconeFait className="size-4 shrink-0" aria-hidden="true" />
                {texte}
              </li>
            ))}
          </ul>
        )}

        {children && <div className="mt-5 flex flex-wrap items-center gap-2.5 border-t border-border/70 pt-5">{children}</div>}
      </div>
    </header>
  )
}
