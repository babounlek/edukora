import { useRef, useState } from "react"
import { Check, Eye, RotateCcw } from "lucide-react"

import type { CoursSectionExempleResolu, CoursSectionExempleResoluEtape } from "@/api/types"
import { BasculeEssai } from "@/components/BasculeEssai"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

type CoursExempleResoluStepsProps = Omit<CoursSectionExempleResolu, "type">

/**
 * La préférence « pas à pas » de l'exemple résolu, mémorisée d'une visite à l'autre (confort d'affichage, jamais une
 * donnée à garantir). ALLUMÉE par défaut, comme le lecteur d'exercice par thème : un exemple se suit, il ne se survole
 * pas - l'élève voit ce qu'on fait, cherche, puis dévoile. « Tout afficher » est à un toucher et se retient.
 */
const CLE = "edukora_cours_exemple_pas_a_pas"

function lirePasAPas(): boolean {
  try {
    return window.localStorage.getItem(CLE) !== "0"
  } catch {
    return true
  }
}

function ecrirePasAPas(valeur: boolean) {
  try {
    window.localStorage.setItem(CLE, valeur ? "1" : "0")
  } catch {
    // stockage indisponible : le mode vaut pour cette visite seulement
  }
}

/** Une étape n'a quelque chose à dévoiler que si elle annonce ce qu'on fait (`action`) ET porte une suite. */
function aDevoiler(etape: CoursSectionExempleResoluEtape): boolean {
  return Boolean(etape.action && (etape.justification || etape.resultat_markdown || etape.body_markdown))
}

/** La première étape, à partir de `depuis`, qui a une suite à dévoiler ; le nombre d'étapes s'il n'en reste aucune. */
function etapeCourante(etapes: CoursSectionExempleResoluEtape[], depuis: number): number {
  for (let i = depuis; i < etapes.length; i++) {
    if (aDevoiler(etapes[i])) return i
  }
  return etapes.length
}

/**
 * Étapes de la section "Exemple résolu" en stepper numéroté, plutôt qu'en "**Étape N**"
 * en gras plat (habillage précédent, hérité du Markdown aplati).
 *
 * Pas à pas (audit 14, C2) : chaque étape montre d'abord ce qu'on fait ; sa justification et son résultat attendent
 * « Voir le résultat », et l'étape suivante n'apparaît qu'ensuite. Aucun contenu à écrire : les cours portent déjà
 * action, justification et résultat. Tout reste dans la page (attribut `hidden`), rien n'est retiré : un moteur de
 * recherche lit l'exemple entier, et le rendu des formules n'est fait qu'une fois.
 *
 * Pas de `not-prose` sur le conteneur : il désactiverait la typographie pour tout le
 * sous-arbre, y compris les `prose` imbriqués ci-dessous, qu'un `prose` ne réactive
 * jamais (voir l'explication détaillée dans CoursRegleBox).
 */
export function CoursExempleResoluSteps({ enonce_markdown, etapes, conclusion_markdown }: CoursExempleResoluStepsProps) {
  useI18n()
  const [pasAPas, setPasAPas] = useState(lirePasAPas)
  // Nombre d'étapes déjà dévoilées par l'élève ; l'étape « courante » est la première qui a encore une suite cachée.
  const [devoilees, setDevoilees] = useState(0)
  const racine = useRef<HTMLDivElement>(null)
  const aChercher = etapes.some(aDevoiler)
  const courante = pasAPas && aChercher ? etapeCourante(etapes, devoilees) : etapes.length
  const fini = courante >= etapes.length

  function changerDeMode(valeur: boolean) {
    setPasAPas(valeur)
    ecrirePasAPas(valeur)
    setDevoilees(0)
  }

  function refaire() {
    setDevoilees(0)
    // L'exemple se replie au-dessus du bouton : sans cela l'écran restait sur la section suivante du cours.
    racine.current?.scrollIntoView?.({ block: "start", behavior: "smooth" })
  }

  return (
    // scroll-mt : passer sous l'en-tête et la barre du sommaire, comme les sections du cours (voir CoursSection).
    <div ref={racine} className="flex scroll-mt-36 flex-col gap-5 lg:scroll-mt-24">
      {aChercher && <BasculeEssai essai={pasAPas} onChange={changerDeMode} className="self-start" />}
      {enonce_markdown && (
        <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
          <EpreuveMarkdown markdown={enonce_markdown} />
        </div>
      )}
      {etapes.length > 0 && (
        <ol className="flex flex-col gap-4">
          {etapes.map((etape, index) => {
            const enAttente = index === courante
            return (
              <li key={index} hidden={index > courante} className={cn("relative flex gap-3", index > 0 && pasAPas && "animate-fade-up")}>
                {index < Math.min(courante, etapes.length - 1) && (
                  <span className="absolute left-3.5 top-8 h-[calc(100%-0.5rem)] w-px bg-border" aria-hidden="true" />
                )}
                <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                  {index + 1}
                </span>
                <div className="flex flex-1 flex-col gap-1.5 pb-2 pt-0.5">
                  {etape.action && (
                    <div className="font-medium [&_p]:m-0">
                      <EpreuveMarkdown markdown={etape.action} />
                    </div>
                  )}
                  <div hidden={enAttente} className={cn("flex flex-col gap-1.5", pasAPas && "animate-fade-up")}>
                    {etape.justification && (
                      <div className="text-sm italic text-muted-foreground [&_p]:m-0">
                        <EpreuveMarkdown markdown={etape.justification} />
                      </div>
                    )}
                    {/* Taille de corps pleine (pas prose-sm) : c'est le résultat de l'étape, souvent
                        une formule, qu'on ne veut pas rapetisser. Pas de `prose-p:my-*` non plus
                        pour compenser le padding serré (px-3 py-2) - cf. CoursErreurCard : un tel
                        override écraserait le reset first/last-child du plugin et ajouterait au
                        contraire de la marge au cas courant (un seul bloc, qui calcule 0). */}
                    {etape.resultat_markdown && (
                      <div className="prose prose-neutral max-w-none rounded-md border border-border bg-muted/40 px-3 py-2 dark:prose-invert">
                        <EpreuveMarkdown markdown={etape.resultat_markdown} />
                      </div>
                    )}
                    {etape.body_markdown && (
                      <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
                        <EpreuveMarkdown markdown={etape.body_markdown} />
                      </div>
                    )}
                  </div>
                  {enAttente && (
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                      <Button type="button" variant="outline" className="min-h-11 rounded-full" onClick={() => setDevoilees(index + 1)}>
                        <Eye className="size-4" aria-hidden="true" />
                        {etape.resultat_markdown ? t("cs.pas_voir_resultat") : t("cs.pas_voir_explication")}
                      </Button>
                      <span className="text-xs text-muted-foreground">{t("cs.pas_etape", { i: index + 1, n: etapes.length })}</span>
                    </div>
                  )}
                </div>
              </li>
            )
          })}
        </ol>
      )}
      {conclusion_markdown && (
        <div hidden={!fini} className="prose prose-neutral max-w-none text-justify dark:prose-invert">
          <EpreuveMarkdown markdown={conclusion_markdown} />
        </div>
      )}
      {pasAPas && aChercher && fini && (
        <div className="animate-fade-up flex flex-wrap items-center gap-x-3 gap-y-2 rounded-xl border border-success/40 bg-success/5 px-4 py-3 text-sm" role="status">
          <span className="flex items-center gap-2 font-medium">
            <Check className="size-4 shrink-0 text-success" aria-hidden="true" />
            {t("cs.pas_fini")}
          </span>
          <Button type="button" variant="ghost" size="sm" className="ml-auto min-h-11 rounded-full" onClick={refaire}>
            <RotateCcw className="size-4" aria-hidden="true" />
            {t("cs.pas_refaire")}
          </Button>
        </div>
      )}
    </div>
  )
}
