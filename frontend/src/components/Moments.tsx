import { useState } from "react"
import { X } from "lucide-react"

import type { Accueil } from "@/api/types"
import { momentsCandidats } from "@/lib/moments"
import { cn } from "@/lib/utils"

/**
 * Un moment - et un seul - quand quelque chose vaut d'être marqué : un palier de
 * travail franchi cette semaine, une série qui atteint 7, 30 ou 100 jours, un thème
 * passé en solide depuis la dernière visite.
 *
 * Sobre et unique par construction : une ligne, une icône, une croix pour la fermer,
 * jamais de confettis. Montré UNE fois (mémoire du navigateur par élève) : rejouer le
 * même palier à chaque ouverture, c'est apprendre à l'élève à ne plus le voir. La
 * priorité entre plusieurs moments va au plus rare (le palier, puis la série, puis le
 * thème), et le reste attend simplement la prochaine visite.
 */
export function Moments({ accueil, userId }: { accueil: Accueil; userId: number | undefined }) {
  const cle = `edukora:moments:${userId ?? "anonyme"}`
  const [vus, setVus] = useState<string[]>(() => lire(cle))
  const moment = momentsCandidats(accueil).find((m) => !vus.includes(m.cle))
  if (!moment) return null

  function fermer() {
    const suivants = [...vus, moment!.cle].slice(-50)
    setVus(suivants)
    try {
      localStorage.setItem(cle, JSON.stringify(suivants))
    } catch {
      // Sans stockage, le moment reviendra à la prochaine ouverture - acceptable.
    }
  }

  const Icone = moment.icone
  return (
    <section className="mx-auto max-w-5xl px-4 pt-4 sm:px-6" aria-label={moment.surtitre}>
      <div
        className={cn(
          "animate-fade-up flex items-center gap-3 rounded-2xl border border-gold/35 bg-gold/[0.08] px-4 py-3",
        )}
      >
        <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-gold/25 text-gold-foreground dark:text-gold-text">
          <Icone className="size-4" aria-hidden="true" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">{moment.surtitre}</span>
          <span className="block truncate text-sm font-medium">{moment.texte}</span>
        </span>
        <button
          type="button"
          onClick={fermer}
          aria-label="Fermer"
          className="rounded-full p-1.5 text-muted-foreground transition-colors hover:bg-gold/15 hover:text-foreground"
        >
          <X className="size-4" />
        </button>
      </div>
    </section>
  )
}

function lire(cle: string): string[] {
  try {
    const brut = localStorage.getItem(cle)
    const lu = brut ? JSON.parse(brut) : []
    return Array.isArray(lu) ? lu.filter((v) => typeof v === "string") : []
  } catch {
    return []
  }
}
