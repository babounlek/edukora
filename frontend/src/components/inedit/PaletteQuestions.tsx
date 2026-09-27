import { useState } from "react"
import { Flag, LayoutGrid } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { cn } from "@/lib/utils"
import { mots, type Unite } from "@/lib/vocabulaire"

export type EtatPastille = "a_traiter" | "traitee" | "a_noter" | "notee"

export interface PastilleQuestion {
  id: number
  label: string
  etat: EtatPastille
  aRevoir: boolean
}

export interface GroupePalette {
  titre: string
  pastilles: PastilleQuestion[]
}

function libelleEtat(unite: Unite): Record<EtatPastille, string> {
  const exercice = unite === "exercice"
  return {
    a_traiter: exercice ? "pas encore traité" : "pas encore traitée",
    traitee: exercice ? "traité" : "traitée",
    a_noter: "à noter",
    notee: exercice ? "noté" : "notée",
  }
}

const STYLE_ETAT: Record<EtatPastille, string> = {
  a_traiter: "border-border text-muted-foreground hover:bg-accent/40",
  traitee: "border-primary bg-primary text-primary-foreground",
  a_noter: "border-warning bg-warning/10 text-foreground",
  notee: "border-success bg-success/15 text-foreground",
}

interface PaletteProps {
  groupes: GroupePalette[]
  courante: number | null
  // Avant la copie rendue on parle de questions traitées ; après, de questions notées.
  rendue: boolean
  unite?: Unite
  onAller: (questionId: number) => void
}

/**
 * La carte de l'épreuve : une pastille par question, colorée selon son état, pour voir d'un
 * coup d'œil ce qui reste et y sauter. Elle ne montre AUCUN énoncé - numéros seulement - donc
 * n'apprend rien sur les questions à venir : c'est le plan de la salle, pas un sommaire.
 */
export function PaletteQuestions({ groupes, courante, rendue, unite = "question", onAller }: PaletteProps) {
  const m = mots(unite)
  const LIBELLE_ETAT = libelleEtat(unite)
  const legende: EtatPastille[] = rendue ? ["a_noter", "notee", "a_traiter"] : ["traitee", "a_traiter"]

  return (
    <nav aria-label="Questions de l'épreuve" className="flex flex-col gap-4">
      {groupes.map((groupe) => (
        <div key={groupe.titre}>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">{groupe.titre}</p>
          <ul className="flex flex-wrap gap-1.5">
            {groupe.pastilles.map((pastille) => (
              <li key={pastille.id}>
                <button
                  type="button"
                  onClick={() => onAller(pastille.id)}
                  aria-current={courante === pastille.id ? "true" : undefined}
                  aria-label={`${groupe.titre}, ${m.singulier} ${pastille.label}, ${LIBELLE_ETAT[pastille.etat]}${pastille.aRevoir ? ", à revoir" : ""}`}
                  className={cn(
                    "relative grid size-10 place-items-center rounded-lg border text-sm font-medium tabular-nums transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
                    STYLE_ETAT[pastille.etat],
                    courante === pastille.id && "ring-2 ring-ring",
                  )}
                >
                  {pastille.label}
                  {pastille.aRevoir && (
                    <Flag
                      aria-hidden="true"
                      className="absolute -right-1 -top-1 size-3.5 fill-gold text-gold-text drop-shadow-sm"
                    />
                  )}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground" aria-label="Légende">
        {legende.map((etat) => (
          <li key={etat} className="flex items-center gap-1.5">
            <span aria-hidden="true" className={cn("size-3 rounded border", STYLE_ETAT[etat].split(" hover")[0])} />
            {LIBELLE_ETAT[etat].replace(/pas encore traitée?/, unite === "exercice" ? "à traiter" : "à traiter")}
          </li>
        ))}
        {!rendue && (
          <li className="flex items-center gap-1.5">
            <Flag aria-hidden="true" className="size-3 fill-gold text-gold-text" />
            à revoir
          </li>
        )}
      </ul>
    </nav>
  )
}

/**
 * Sur mobile la palette n'a pas de colonne où vivre : un bouton discret sous la barre d'état
 * l'ouvre en feuille basse, à portée du pouce.
 */
export function BoutonPalette({
  groupes, courante, rendue, unite = "question", onAller, resume,
}: PaletteProps & { resume: string }) {
  const m = mots(unite)
  const Titre = `${m.pluriel[0].toUpperCase()}${m.pluriel.slice(1)}`
  const [ouvert, setOuvert] = useState(false)
  return (
    <>
      <Button variant="outline" size="sm" className="w-full lg:hidden" onClick={() => setOuvert(true)}>
        <LayoutGrid className="size-3.5" />
        {Titre} · {resume}
      </Button>
      <Dialog open={ouvert} onOpenChange={setOuvert}>
        <DialogContent>
          <DialogTitle>{Titre}</DialogTitle>
          <DialogDescription>Touche {m.singulier === "exercice" ? "un" : "une"} {m.singulier} pour y aller.</DialogDescription>
          <div className="mt-4">
            <PaletteQuestions
              groupes={groupes}
              courante={courante}
              rendue={rendue}
              unite={unite}
              onAller={(id) => {
                setOuvert(false)
                window.requestAnimationFrame(() => onAller(id))
              }}
            />
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
