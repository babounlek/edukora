import type { ComponentType } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, BookOpen, CircleHelp, PenLine, Sparkles } from "lucide-react"

import type { ResultatRecherche } from "@/api/types"
import { Surbrillance } from "@/components/recherche/Surbrillance"
import { Button } from "@/components/ui/button"
import { actionsTheme, type ActionTheme } from "@/lib/recherche"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { cn } from "@/lib/utils"

const ICONES: Record<ActionTheme["cle"], ComponentType<{ className?: string }>> = {
  cours: BookOpen,
  exercices: PenLine,
  quiz: CircleHelp,
}

/** « cours », « exercice(s) », « question(s) de quiz » - accordé avec le nombre. */
function unite(action: ActionTheme): string {
  if (action.cle === "cours") return "cours"
  if (action.cle === "exercices") return action.nb > 1 ? "exercices" : "exercice"
  return action.nb > 1 ? "questions de quiz" : "question de quiz"
}

/** « 65 cours, 57 exercices et 12 questions de quiz t'attendent sur ce thème. » */
function phrase(actions: ActionTheme[]): string {
  const morceaux = actions.map((a) => `${a.nb} ${unite(a)}`)
  if (morceaux.length === 0) return ""
  const liste = morceaux.length === 1 ? morceaux[0] : `${morceaux.slice(0, -1).join(", ")} et ${morceaux[morceaux.length - 1]}`
  return `${liste} t'attendent sur ce thème.`
}

/**
 * Le meilleur thème trouvé, mis en avant avec de quoi AGIR tout de suite : trois tuiles chiffrées (cours,
 * exercices, quiz) qui mènent chacune à sa page, et un bouton principal - le quiz d'abord, parce que
 * se tester est la façon la plus rapide de savoir où on en est, sinon les cours. Une liste de
 * résultats répond à « qu'est-ce qui existe ? » ; cette carte répond à « par où je commence ? ».
 */
export function ResultatVedette({
  resultat, jetons, country, onChoisir,
}: {
  resultat: ResultatRecherche
  jetons: string[]
  country: string
  onChoisir?: () => void
}) {
  const actions = actionsTheme(country, resultat)
  const couleur = couleurMatiere(resultat.matiere.code)
  const principale = actions.find((a) => a.cle === "quiz") ?? actions[0]
  const examens = resultat.cursus.slice(0, 4).map((c) => c.label)
  return (
    <section
      aria-labelledby="vedette-titre"
      className="animate-fade-up relative mt-6 overflow-hidden rounded-2xl border border-primary/25 bg-gradient-to-br from-primary/[0.09] via-card to-card p-5 shadow-sm sm:p-6"
    >
      <span className={cn("absolute inset-y-0 left-0 w-1.5", couleur.barre)} aria-hidden="true" />
      <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
        <Sparkles className="size-3.5" aria-hidden="true" />
        Commence par ici
      </p>
      <h2 id="vedette-titre" className="mt-2 font-display text-2xl font-semibold leading-tight tracking-tight sm:text-3xl">
        <Surbrillance texte={resultat.titre} jetons={jetons} />
      </h2>
      <p className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted-foreground">
        <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", couleur.puce)}>{resultat.matiere.label}</span>
        {examens.length > 0 && <span>{examens.join(" · ")}{resultat.cursus_total > examens.length && ` +${resultat.cursus_total - examens.length}`}</span>}
      </p>
      {actions.length > 0 && <p className="mt-3 text-sm text-foreground/80">{phrase(actions)}</p>}

      {actions.length > 0 && (
        <ul className={cn("mt-4 grid gap-2 sm:gap-3", actions.length === 1 ? "grid-cols-1" : actions.length === 2 ? "grid-cols-2" : "grid-cols-3")}>
          {actions.map((action) => {
            const Icone = ICONES[action.cle]
            return (
              <li key={action.cle}>
                <Link
                  to={action.to}
                  onClick={onChoisir}
                  className="group flex h-full flex-col items-start gap-1 rounded-xl border border-border bg-background/80 p-3 transition-all hover:-translate-y-0.5 hover:border-primary/50 hover:shadow-sm motion-reduce:transition-none motion-reduce:hover:translate-y-0"
                >
                  <span className={cn("flex size-7 items-center justify-center rounded-lg", couleur.puce)}>
                    <Icone className="size-4" />
                  </span>
                  <span className="font-display text-2xl font-semibold leading-none">{action.nb}</span>
                  <span className="text-xs text-muted-foreground">{unite(action)}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      )}

      {principale && (
        <Button asChild size="lg" className="mt-4 w-full sm:w-auto">
          <Link to={principale.to} onClick={onChoisir}>
            {principale.cle === "quiz" ? "Tester mes connaissances" : principale.cle === "cours" ? "Ouvrir les cours" : "Faire des exercices"}
            <ArrowRight />
          </Link>
        </Button>
      )}
    </section>
  )
}
