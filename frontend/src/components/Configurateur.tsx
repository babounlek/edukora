import type { ReactNode } from "react"
import { Check } from "lucide-react"

import { cn } from "@/lib/utils"

/** Amorce éditoriale (filet or + libellé en italique serif) réutilisée devant chaque
 * titre de section - même motif que la page "À propos", pour que Fiches et Quiz
 * partagent son vocabulaire visuel au lieu de rester des pages utilitaires isolées. */
export function Eyebrow({ children }: { children: ReactNode }) {
  return (
    <p className="mb-3 flex items-center gap-2.5 font-display text-sm italic text-primary">
      <span className="h-px w-8 bg-gold" />
      {children}
    </p>
  )
}

/** Pastille statistique en pilule (badges du hero) - factorisée hors de
 * FichesPage/QuizStartPage où le même balisage était dupliqué à l'identique pour
 * chaque puce (PDF générés, add-on actif, maîtrise moyenne...). */
export function StatChip({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm shadow-xs">
      {icon}
      {children}
    </span>
  )
}

/**
 * Aperçu "comment ça marche" en trois puces numérotées, affiché avant le
 * configurateur lui-même (voir FichesPage/QuizStartPage) - la même structure
 * numéro-titre que les étapes qui suivent, en plus léger : pas de carte, pas de
 * contenu interactif, juste de quoi situer ce qui va suivre avant de s'y engager.
 */
export function EtapesPresentation({ etapes }: { etapes: string[] }) {
  return (
    <ol className="grid gap-3 sm:grid-cols-3">
      {etapes.map((etape, index) => (
        <li key={index} className="flex items-start gap-2.5 text-sm text-muted-foreground">
          <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
            {index + 1}
          </span>
          {etape}
        </li>
      ))}
    </ol>
  )
}

interface EtapeProps {
  numero: number
  titre: string
  aide?: string
  /** Étape déjà renseignée - le badge numéro passe en coche verte. */
  fait?: boolean
  /** Étape pas encore accessible (dépend d'un choix précédent) - contenu assombri et
   * non interactif plutôt que masqué : l'élève voit ce qui l'attend. */
  inactif?: boolean
  /** Teinte du badge numéro pour une étape prioritaire (ex. "à réviser" du Parcours) -
   * distincte du bleu neutre par défaut, pour repérer l'urgent d'un simple balayage de
   * la liste. Sans effet si `fait` ou `inactif` (qui gardent leur propre couleur). */
  accent?: "gold"
  /** Dernière étape de la séquence - pas de trait de liaison vers une suivante. */
  dernier?: boolean
  children: ReactNode
}

/**
 * Une étape du configurateur (Fiches comme Quiz) : badge numéro/coche relié à la
 * suivante par un trait vertical, titre, aide optionnelle, contenu. `inactif` grise le
 * bloc sans le retirer du flux - l'élève voit toujours qu'une 3e étape existe même
 * s'il n'a pas encore rempli la 1re.
 */
export function Etape({ numero, titre, aide, fait, inactif, accent, dernier, children }: EtapeProps) {
  return (
    <div className={cn("relative flex gap-4", !dernier && "pb-6")}>
      {!dernier && (
        <span
          className={cn("absolute left-[15px] top-8 bottom-0 w-px", fait ? "bg-primary/40" : "bg-border")}
          aria-hidden="true"
        />
      )}
      <span
        className={cn(
          "flex size-8 shrink-0 items-center justify-center rounded-full font-display text-sm font-semibold tabular-nums transition-colors",
          fait
            ? "bg-primary text-primary-foreground"
            : inactif
              ? "bg-muted text-muted-foreground"
              : accent === "gold"
                ? "bg-gold/15 text-gold"
                : "bg-primary/10 text-primary",
        )}
      >
        {fait ? <Check className="size-4" /> : numero}
      </span>
      <div className={cn("min-w-0 flex-1", inactif && "pointer-events-none opacity-50")}>
        <p className="font-display font-semibold">{titre}</p>
        {aide && <p className="mt-0.5 text-sm text-muted-foreground">{aide}</p>}
        <div className="mt-3">{children}</div>
      </div>
    </div>
  )
}

/** Une ligne label/valeur du récapitulatif, à droite du configurateur. */
export function LigneRecap({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-medium">{children}</span>
    </div>
  )
}

/** Placeholder d'une valeur de récapitulatif pas encore choisie - un tiret plutôt
 * qu'un blanc, pour que la ligne reste lisible comme "en attente" et non comme un bug
 * d'affichage. */
export function RecapVide() {
  return <span className="text-muted-foreground">—</span>
}
