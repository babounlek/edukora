import type { ReactNode } from "react"

import { pourcent } from "@/lib/maitrise"
import { STATUTS, type StatutProgression } from "@/lib/statutsProgression"
import { cn } from "@/lib/utils"

/**
 * Le langage visuel partagé par les écrans "coach" - séance du jour, Où j'en suis sur
 * l'accueil, page Ma progression. Un seul fichier pour que les trois ne divergent pas
 * au fil des retouches : un même pourcentage doit se lire pareil partout.
 */

/**
 * La carte des blocs qui comptent. `accent` : filet dégradé vert → or en tête et deux
 * halos, pour LE bloc principal d'un écran (la séance, le haut de Ma progression).
 * `sobre` : un seul halo discret, pour un bloc qui doit rester second à côté.
 */
export function Ecrin({
  children, variante = "accent", className,
}: { children: ReactNode; variante?: "accent" | "sobre"; className?: string }) {
  return (
    <div
      className={cn(
        "animate-fade-up relative overflow-hidden rounded-3xl bg-card p-5 sm:p-8",
        variante === "accent"
          ? "border border-primary/20 shadow-xl shadow-primary/[0.07]"
          : "border border-border/80 shadow-lg shadow-primary/[0.04]",
        className,
      )}
    >
      {variante === "accent" ? (
        <>
          <div aria-hidden className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary via-gold to-primary/30" />
          <div aria-hidden className="pointer-events-none absolute -right-28 -top-28 size-80 rounded-full bg-primary/[0.09] blur-3xl" />
          <div aria-hidden className="pointer-events-none absolute -bottom-36 -left-20 size-72 rounded-full bg-gold/[0.08] blur-3xl" />
        </>
      ) : (
        <div aria-hidden className="pointer-events-none absolute -left-24 -top-24 size-64 rounded-full bg-primary/[0.06] blur-3xl" />
      )}
      <div className="relative">{children}</div>
    </div>
  )
}

/** Anneau SVG plutôt qu'une bibliothèque de graphiques : un seul arc, et il doit
 * suivre les couleurs du thème clair/sombre via les tokens. */
export function AnneauProgression({ part, className }: { part: number; className?: string }) {
  const rayon = 30
  const circonference = 2 * Math.PI * rayon
  return (
    <div
      className={cn("relative size-20 shrink-0 sm:size-24", className)}
      role="img"
      aria-label={`${pourcent(part)} % maîtrisé`}
    >
      <svg viewBox="0 0 72 72" className="size-full -rotate-90">
        <circle cx="36" cy="36" r={rayon} fill="none" strokeWidth="7" className="stroke-muted" />
        <circle
          cx="36" cy="36" r={rayon} fill="none" strokeWidth="7" strokeLinecap="round"
          className="stroke-primary transition-[stroke-dashoffset] duration-700"
          strokeDasharray={circonference}
          // Un arc de longueur nulle avec des bouts arrondis dessine quand même un
          // point : à 0 %, on le masque plutôt que d'afficher un progrès inexistant.
          strokeDashoffset={circonference * (1 - Math.min(1, part))}
          opacity={part > 0 ? 1 : 0}
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center font-display text-lg font-semibold tabular-nums sm:text-xl">
        {pourcent(part)}
        <span className="ml-px text-xs font-medium text-muted-foreground">%</span>
      </span>
    </div>
  )
}

/**
 * Maîtrisé (vert), en révision (or), en cours (bleu), le reste du rail = à découvrir.
 * Une barre à un seul segment restait vide pour presque tout le monde au démarrage ;
 * les segments montrent que le travail en cours compte déjà, avant la première
 * maîtrise.
 *
 * "En cours" (bleu, `enCours`) est distinct de "à découvrir" (gris, l'espace non
 * rempli) : un thème déjà pratiqué au moins une fois, mais ni maîtrisé ni
 * actuellement dû en révision - typiquement un thème qui a gradué hors de la file de
 * révision (Leitner) sans que sa moyenne historique ait franchi le seuil de maîtrise.
 * Sans ce segment, ce travail redevenait invisible, indiscernable d'un thème jamais
 * ouvert (voir quiz.services.resume_parcours côté backend, et ResumeMatiere.en_cours).
 */
export function BarreSegmentee({
  maitrises, enRevision, enCours = 0, exploitables, className,
}: { maitrises: number; enRevision: number; enCours?: number; exploitables: number; className?: string }) {
  const largeur = (n: number) => `${exploitables > 0 ? pourcent(n / exploitables) : 0}%`
  return (
    <div
      className={cn("flex h-2 gap-0.5 overflow-hidden rounded-full bg-muted", className)}
      role="img"
      aria-label={
        `${maitrises} maîtrisés, ${enRevision} en révision, ${enCours} en cours, `
        + `${Math.max(0, exploitables - maitrises - enRevision - enCours)} à découvrir`
      }
    >
      <span className={cn("h-full rounded-full transition-all duration-700", STATUTS.maitrise.barre)} style={{ width: largeur(maitrises) }} />
      <span className={cn("h-full rounded-full transition-all duration-700", STATUTS.en_revision.barre)} style={{ width: largeur(enRevision) }} />
      <span className={cn("h-full rounded-full transition-all duration-700", STATUTS.en_cours.barre)} style={{ width: largeur(enCours) }} />
    </div>
  )
}

/** Légende : chaque statut avec son icône ET sa couleur - jamais la couleur seule. */
export function LegendeProgression() {
  const ordre: StatutProgression[] = ["maitrise", "en_revision", "en_cours", "a_decouvrir"]
  return (
    <p className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-muted-foreground">
      {ordre.map((statut) => {
        const { libelle, Icone, puce } = STATUTS[statut]
        return (
          <span key={statut} className="flex items-center gap-1.5">
            <span className={cn("flex size-4 items-center justify-center rounded-full", puce)}>
              <Icone className="size-2.5" strokeWidth={3} aria-hidden="true" />
            </span>
            {libelle}
          </span>
        )
      })}
    </p>
  )
}

/** Un compteur de statut : le chiffre en grand, et l'icône de son statut (la même que dans la
 * légende, les badges et la frise). `libelle` remplace celui du statut quand la page a son mot
 * ("À réviser" plutôt que "En révision"). */
export function CompteurStatut({
  statut, valeur, libelle,
}: { statut: StatutProgression; valeur: number; libelle?: string }) {
  const { libelle: libelleStatut, Icone, puce } = STATUTS[statut]
  return (
    <div className="rounded-2xl border border-border/70 bg-background/70 px-3 py-3 backdrop-blur-sm sm:px-4">
      <p className="flex items-center gap-2 whitespace-nowrap text-xs text-muted-foreground">
        <span className={cn("flex size-5 shrink-0 items-center justify-center rounded-full", puce)}>
          <Icone className="size-3" strokeWidth={3} aria-hidden="true" />
        </span>
        {libelle ?? libelleStatut}
      </p>
      <p className="mt-1.5 font-display text-2xl font-semibold tabular-nums sm:text-3xl">{valeur}</p>
    </div>
  )
}
