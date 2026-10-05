import type { ComponentType } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, BookOpen, Check, CircleHelp, FileText, Lock, PenLine, Sparkles, Tag } from "lucide-react"

import type { ResultatRecherche as Resultat, TypeResultatRecherche } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Surbrillance } from "@/components/recherche/Surbrillance"
import { actionsTheme, cibleResultat, LIBELLES_TYPE } from "@/lib/recherche"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { cn } from "@/lib/utils"

const ICONES: Record<TypeResultatRecherche, ComponentType<{ className?: string }>> = {
  THEME: Tag,
  COURS: BookOpen,
  EPREUVE: FileText,
  INEDITE: Sparkles,
  EXERCICE: PenLine,
  QUIZ: CircleHelp,
}

/** Pictogramme d'un type de résultat (thème, cours, épreuve...). */
export function IconeType({ type, className }: { type: TypeResultatRecherche; className?: string }) {
  const Icone = ICONES[type]
  return <Icone className={className} aria-hidden="true" />
}

/** Ce que fait le lien d'un résultat, dit en un verbe - une carte qui dit « Lire le cours » invite plus
 * à cliquer qu'un titre seul. */
const VERBE: Record<TypeResultatRecherche, string> = {
  THEME: "Explorer ce thème",
  COURS: "Lire le cours",
  EPREUVE: "Voir l'épreuve",
  INEDITE: "Découvrir l'épreuve",
  EXERCICE: "Voir l'exercice",
  QUIZ: "S'entraîner",
}

/** « BAC C · BAC E +2 », « Tous les examens » - les examens auxquels le résultat est proposé. */
function libelleExamens(resultat: Resultat): string {
  if (resultat.cursus.length === 0) return resultat.tous_cursus ? "Tous les examens" : ""
  const visibles = resultat.cursus.slice(0, 3).map((c) => c.label).join(" · ")
  const reste = resultat.cursus_total - Math.min(resultat.cursus.length, 3)
  return reste > 0 ? `${visibles} +${reste}` : visibles
}

/** Ce qu'on dit d'un résultat en une ligne : « Cours · Mathématiques · BAC C · 2019 ». */
function ligneMeta(resultat: Resultat): string {
  const parties = [
    resultat.type === "EPREUVE" && resultat.details.type_libelle ? resultat.details.type_libelle : LIBELLES_TYPE[resultat.type].singulier,
    resultat.matiere.label,
    libelleExamens(resultat),
  ]
  return parties.filter(Boolean).join(" · ")
}

/** L'indice d'accès, en mots : « Gratuit », « Inclus » (ce visiteur y a droit) ou « Abonnés ». Un simple
 * indice - c'est la page du contenu qui applique la vraie règle. */
export function IndiceAcces({ resultat, compact = false }: { resultat: Resultat; compact?: boolean }) {
  if (resultat.acces === "libre") return <Badge variant="success">Gratuit</Badge>
  if (resultat.acces === "ouvert") {
    return compact ? null : (
      <span className="inline-flex shrink-0 items-center gap-1 text-xs font-medium text-primary">
        <Check className="size-3.5" aria-hidden="true" />
        Inclus
      </span>
    )
  }
  if (resultat.acces === "verrouille") {
    return (
      <span
        className="inline-flex shrink-0 items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
        title="Réservé aux abonnés"
      >
        <Lock className="size-3" aria-hidden="true" />
        {compact ? <span className="sr-only">Réservé aux abonnés</span> : "Abonnés"}
      </span>
    )
  }
  return null
}

/** Résumé chiffré d'un thème : « 3 cours · 12 questions ». */
function resumeTheme(resultat: Resultat): string {
  const { nb_cours = 0, nb_quiz = 0, nb_exercices = 0 } = resultat.details
  return [
    nb_cours > 0 && `${nb_cours} cours`,
    nb_exercices > 0 && `${nb_exercices} exercice${nb_exercices > 1 ? "s" : ""}`,
    nb_quiz > 0 && `${nb_quiz} question${nb_quiz > 1 ? "s" : ""}`,
  ]
    .filter(Boolean)
    .join(" · ")
}

interface Props {
  resultat: Resultat
  jetons: string[]
  country: string
  /** Appelé quand l'élève choisit ce résultat (clic) - pour fermer la palette, mémoriser la recherche. */
  onChoisir?: () => void
}

/** Une ligne de la palette de recherche : compacte, tout le résultat est un seul lien. */
export function ResultatCompact({
  resultat, jetons, country, onChoisir, id, actif,
}: Props & { id: string; actif: boolean }) {
  const sousTitre = resultat.type === "THEME" ? [resultat.matiere.label, resumeTheme(resultat)].filter(Boolean).join(" · ") : ligneMeta(resultat)
  return (
    <Link
      id={id}
      role="option"
      aria-selected={actif}
      to={cibleResultat(country, resultat)}
      onClick={onChoisir}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-left outline-none",
        actif ? "bg-accent text-accent-foreground" : "hover:bg-accent/60",
      )}
    >
      <span className={cn("flex size-8 shrink-0 items-center justify-center rounded-md", couleurMatiere(resultat.matiere.code).puce)}>
        <IconeType type={resultat.type} className="size-4" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-medium">
          <Surbrillance texte={resultat.titre} jetons={jetons} />
        </span>
        <span className="block truncate text-xs text-muted-foreground">{sousTitre}</span>
      </span>
      <IndiceAcces resultat={resultat} compact />
    </Link>
  )
}

/**
 * Une carte de la page de résultats : bande de la couleur de la matière (on reconnaît « les maths »
 * d'un coup d'œil), titre, contexte, extrait surligné, indice d'accès et un verbe d'action. Toute la
 * carte est cliquable (lien étendu sur le titre) ; pour un thème, les trois façons de le travailler
 * restent des liens à part, posés AU-DESSUS du lien étendu.
 */
export function ResultatCarte({ resultat, jetons, country, onChoisir }: Props) {
  const actions = resultat.type === "THEME" ? actionsTheme(country, resultat) : []
  const couleur = couleurMatiere(resultat.matiere.code)
  const meta = ligneMeta(resultat)
  const annee = resultat.annee && !resultat.titre.includes(String(resultat.annee)) ? String(resultat.annee) : ""
  return (
    <article className="group relative overflow-hidden rounded-xl border border-border bg-card p-4 pl-5 shadow-xs transition-all hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-md focus-within:border-primary/40 motion-reduce:transition-none motion-reduce:hover:translate-y-0">
      <span className={cn("absolute inset-y-0 left-0 w-1", couleur.barre)} aria-hidden="true" />
      <div className="flex items-start gap-3">
        <span className={cn("mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg", couleur.puce)}>
          <IconeType type={resultat.type} className="size-[18px]" />
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-base font-semibold leading-snug">
            <Link
              to={cibleResultat(country, resultat)}
              onClick={onChoisir}
              className="outline-none after:absolute after:inset-0 after:content-[''] group-hover:text-primary"
            >
              <Surbrillance texte={resultat.titre} jetons={jetons} />
            </Link>
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground">
            {meta}
            {annee && ` · ${annee}`}
          </p>
          {resultat.type === "QUIZ" && resultat.nb !== null && resultat.nb > 0 && (
            <p className="mt-1 text-xs font-medium text-foreground/80">
              {resultat.nb} question{resultat.nb > 1 ? "s" : ""} correspondent
            </p>
          )}
          {resultat.apercu ? (
            <p className="mt-2 text-sm leading-relaxed text-foreground/80">
              <Surbrillance texte={resultat.apercu} jetons={jetons} />
            </p>
          ) : resultat.type === "QUIZ" && resultat.acces === "verrouille" ? (
            <p className="mt-2 text-sm text-muted-foreground">Questions réservées aux abonnés.</p>
          ) : null}
          {actions.length > 0 && (
            <ul className="relative z-10 mt-3 flex flex-wrap gap-2">
              {actions.map((action) => (
                <li key={action.cle}>
                  <Link
                    to={action.to}
                    onClick={onChoisir}
                    className="inline-flex items-center rounded-full border border-border bg-background px-3 py-1 text-xs font-medium transition-colors hover:border-primary hover:text-primary"
                  >
                    {action.libelle}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="flex shrink-0 flex-col items-end gap-2">
          <IndiceAcces resultat={resultat} />
          <span className="mt-auto hidden items-center gap-1 text-xs font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 sm:inline-flex">
            {VERBE[resultat.type]}
            <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
          </span>
        </div>
      </div>
    </article>
  )
}
