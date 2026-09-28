import { Link } from "react-router-dom"
import { ArrowRight, type LucideIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import type { ReactNode } from "react"

/**
 * Vocabulaire visuel commun aux pages reliées au menu du compte (Mon compte, Mes accès, Mon
 * historique, Mes paiements) : même largeur de page (max-w-5xl), même carte d'en-tête (icône dans
 * un rond, titre, sous-titre) et mêmes cartes de contenu - pour qu'on sente qu'on reste dans la
 * même zone de l'appli en passant de l'une à l'autre via le menu déroulant du header, plutôt que
 * de changer de gabarit à chaque clic.
 */

/** L'en-tête d'une page du compte : icône dans un rond, titre, sous-titre - même forme que la
 * carte de profil de /compte (qui met des initiales à la place de l'icône). */
export function EnteteCompte({
  icone: Icone, titre, sousTitre,
}: { icone: LucideIcon; titre: string; sousTitre: string }) {
  return (
    <section className="mb-5 flex items-center gap-3.5 rounded-2xl border border-border bg-card p-4 sm:p-5">
      <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
        <Icone className="size-5" aria-hidden="true" />
      </span>
      <div className="min-w-0 flex-1">
        <h1 className="font-display text-lg font-semibold leading-tight">{titre}</h1>
        <p className="text-sm text-muted-foreground">{sousTitre}</p>
      </div>
    </section>
  )
}

/** Une section : titre avec pastille d'icône, action à droite, contenu dans une carte discrète. */
export function Section({
  icone: Icone, titre, action, children, className,
}: { icone: LucideIcon; titre: string; action?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={cn("rounded-2xl border border-border bg-card p-4 sm:p-5", className)}>
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 font-display text-base font-semibold">
          <Icone className="size-4 text-primary" aria-hidden="true" />
          {titre}
        </h2>
        {action}
      </div>
      {children}
    </section>
  )
}

/** Un état vide qui propose la suite plutôt que de constater le vide. */
export function EtatVide({
  texte, lien, libelleLien,
}: { texte: string; lien: string; libelleLien: string }) {
  return (
    <div className="rounded-xl border border-dashed border-border bg-muted/30 px-4 py-4 text-center">
      <p className="text-sm text-muted-foreground">{texte}</p>
      <Link to={lien} className="mt-1.5 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline">
        {libelleLien}
        <ArrowRight className="size-3.5" />
      </Link>
    </div>
  )
}
