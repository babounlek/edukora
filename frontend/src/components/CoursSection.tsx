import { useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { Lock } from "lucide-react"

import type { CoursSectionData, CoursSectionExerciceItem } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { SolutionToggle } from "@/components/SolutionToggle"
import { CoursRegleBox } from "@/components/CoursRegleBox"
import { CoursExempleResoluSteps } from "@/components/CoursExempleResoluSteps"
import { CoursErreurCard } from "@/components/CoursErreurCard"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { t, tn } from "@/lib/i18n"
import { libelleNiveauExercice } from "@/lib/libellesEpreuve"

/** Libellés partagés entre le sommaire (CoursSommaire) et les titres de section ci-dessous - "short" pour une pastille compacte, "full" pour le titre en page. Jamais d'entrée pour "accroche" : ce n'est pas une section navigable, juste le texte d'ouverture. */
export const COURS_SECTION_LABELS: Partial<Record<CoursSectionData["type"], { short: string; full: string }>> = {
  // Des accesseurs plutôt que des chaînes : le libellé suit la langue au moment où il est lu.
  prerequis: { get short() { return t("cs.prerequis") }, get full() { return t("cs.prerequis") } },
  regle: { get short() { return t("cs.regle") }, get full() { return t("cs.regle") } },
  exemple_resolu: { get short() { return t("cs.exemple_resolu") }, get full() { return t("cs.exemple_resolu") } },
  erreurs_classiques: { get short() { return t("cs.erreurs_classiques") }, get full() { return t("cs.erreurs_classiques") } },
  exercices_application: { get short() { return t("cs.exercices_court") }, get full() { return t("cs.exercices_long") } },
  synthese: { get short() { return t("cs.synthese_court") }, get full() { return t("cs.synthese_long") } },
}

// Au-delà, l'accroche est repliée : onze lignes d'italique avant la règle du cours faisaient fuir un élève qui vient pour la
// méthode (test élève Guyguy). Une longueur en caractères, faute de pouvoir mesurer les lignes avant le rendu.
const ACCROCHE_LONGUE = 280

function Accroche({ markdown }: { markdown: string }) {
  const [ouverte, setOuverte] = useState(false)
  const longue = markdown.length > ACCROCHE_LONGUE
  return (
    <div>
      <div className="relative">
        <div
          className={cn(
            "font-display text-lg italic leading-relaxed text-justify text-foreground sm:text-xl",
            longue && !ouverte && "max-h-32 overflow-hidden",
          )}
        >
          <EpreuveMarkdown markdown={markdown} />
        </div>
        {longue && !ouverte && (
          <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-background to-transparent" />
        )}
      </div>
      {longue && (
        <button
          type="button"
          aria-expanded={ouverte}
          onClick={() => setOuverte(!ouverte)}
          className="mt-1 text-sm font-medium text-primary underline-offset-4 hover:underline"
        >
          {ouverte ? t("cs.accroche_reduire") : t("cs.accroche_suite")}
        </button>
      )}
    </div>
  )
}

/**
 * Section « exercices d'application » d'un lecteur sans abonnement : le serveur ne l'a pas envoyée, il l'a remplacée par
 * un marqueur (nombre d'exercices et niveaux). La carte dit ce qui attend l'abonné sans en montrer une ligne.
 */
function ExercicesVerrouilles({ nb, difficultes, lienAbonnement }: { nb: number; difficultes: string[]; lienAbonnement: string }) {
  return (
    <div className="flex flex-col items-start gap-3 rounded-lg border border-dashed border-border bg-muted/40 p-4">
      <p className="flex items-center gap-2 font-medium">
        <Lock className="size-4 text-muted-foreground" aria-hidden="true" />
        {tn("cs.verrou", nb)}
      </p>
      {difficultes.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {difficultes.map((difficulte, index) => (
            <Badge key={`${difficulte}-${index}`} variant="outline" className="capitalize">{libelleNiveauExercice(difficulte)}</Badge>
          ))}
        </div>
      )}
      <p className="text-sm text-muted-foreground">{t("cs.verrou_texte")}</p>
      <Button asChild size="sm">
        <Link to={lienAbonnement}>{t("prix.sabonner")}</Link>
      </Button>
    </div>
  )
}

function CoursExerciceApplicationItem({ item, index }: { item: CoursSectionExerciceItem; index: number }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <p className="font-medium">{t("ed.exercice_n", { n: item.numero ?? index + 1 })}</p>
        {item.difficulte && <Badge variant="outline" className="capitalize">{libelleNiveauExercice(item.difficulte)}</Badge>}
      </div>
      <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
        <EpreuveMarkdown markdown={item.enonce_markdown} />
      </div>
      {item.solution_markdown && (
        <SolutionToggle>
          <EpreuveMarkdown markdown={item.solution_markdown} />
        </SolutionToggle>
      )}
    </div>
  )
}

/**
 * Rend une section de Cours.sections_breakdown() avec l'habillage propre à son type -
 * contrairement à l'ancien pipeline (content_markdown aplati passé tel quel à
 * EpreuveMarkdown), où règle/exemple résolu/erreurs classiques n'avaient pas plus de
 * poids visuel qu'un paragraphe. `id={section.type}` sert d'ancre au sommaire
 * (CoursSommaire) - un Cours ne porte jamais deux sections du même type.
 *
 * `lienAbonnement` : où mène le bouton de la carte « exercices d'application verrouillés » (voir
 * ExercicesVerrouilles) - le lecteur y met le lien d'abonnement du cursus du cours.
 *
 * `pied` : ce que le lecteur ajoute en bas de section (outils d'étude : compris, signet,
 * note) - jamais rendu pour l'accroche, qui n'est pas une section navigable.
 */
export function CoursSection({ section, pied, lienAbonnement = "/tarifs" }: { section: CoursSectionData; pied?: ReactNode; lienAbonnement?: string }) {
  if (section.type === "accroche") {
    return <Accroche markdown={section.body_markdown} />
  }

  const label = COURS_SECTION_LABELS[section.type]

  return (
    // scroll-mt-36 sous `lg` : l'ancre doit passer sous le Header (72 px) ET la barre de pastilles
    // du sommaire (≈ 57 px, voir SommaireNav) ; au-delà, seule la sidebar existe, 24 suffit.
    <section id={section.type} className="scroll-mt-36 lg:scroll-mt-24">
      {label && <h2 className="mb-3 font-display text-xl font-semibold">{label.full}</h2>}

      {section.type === "prerequis" && (
        <ul className="not-prose flex flex-col gap-1.5">
          {section.items.map((item, index) => (
            <li key={index} className="flex items-center gap-1.5 text-sm">
              <span className="text-muted-foreground" aria-hidden="true">•</span>
              {item.cours_slug ? (
                <Link to={`/cours/${item.cours_slug}`} className="font-medium text-primary hover:underline">
                  <EpreuveMarkdown markdown={item.label} />
                </Link>
              ) : (
                <EpreuveMarkdown markdown={item.label} />
              )}
            </li>
          ))}
        </ul>
      )}

      {section.type === "regle" && <CoursRegleBox {...section} />}
      {section.type === "exemple_resolu" && <CoursExempleResoluSteps {...section} />}

      {section.type === "erreurs_classiques" && (
        <div className="flex flex-col gap-3">
          {section.items.map((item, index) => (
            <CoursErreurCard key={index} {...item} />
          ))}
        </div>
      )}

      {section.type === "exercices_application" && section.verrouille && (
        <ExercicesVerrouilles nb={section.nb_exercices ?? 0} difficultes={section.difficultes ?? []} lienAbonnement={lienAbonnement} />
      )}

      {section.type === "exercices_application" && !section.verrouille && (
        <div className="flex flex-col gap-6">
          {section.items.map((item, index) => (
            <CoursExerciceApplicationItem key={index} item={item} index={index} />
          ))}
        </div>
      )}

      {/* Pas de `not-prose` sur la carte : il désactiverait la typographie pour tout le
          sous-arbre, y compris le `prose` juste en dessous, qu'un `prose` imbriqué ne
          réactive jamais (voir l'explication détaillée dans CoursRegleBox) - or "Ce
          qu'il faut retenir" est justement une liste à puces, qui perdait retrait et
          puces. Le `not-prose` du <ul> des prérequis plus haut reste légitime, lui :
          rien sous cet élément ne réclame la typographie de prose. */}
      {section.type === "synthese" && (
        <div className="rounded-lg border border-border bg-muted/40 p-4">
          <div className="prose prose-neutral max-w-none dark:prose-invert">
            <EpreuveMarkdown markdown={section.body_markdown} />
          </div>
        </div>
      )}

      {pied}
    </section>
  )
}
