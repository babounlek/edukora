import { useState } from "react"
import { Flag, LayoutGrid } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { cn } from "@/lib/utils"
import { tu, libellesUnite, type Unite } from "@/lib/vocabulaire"
import { t, useI18n } from "@/lib/i18n"

// Après la copie rendue, une QCM est « juste » ou « fausse » (on la voit tout de suite) ; une question jamais traitée est « non_faite » :
// elle ne se confond ni avec une faute ni avec une question encore à faire.
export type EtatPastille = "a_traiter" | "traitee" | "a_noter" | "notee" | "juste" | "fausse" | "non_faite"

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
  return {
    a_traiter: tu("pa.a_traiter", unite),
    traitee: tu("pa.traitee", unite),
    a_noter: t("pa.a_noter"),
    notee: tu("pa.notee", unite),
    juste: t("pa.juste"),
    fausse: t("pa.fausse"),
    non_faite: tu("pa.non_faite", unite),
  }
}

const STYLE_ETAT: Record<EtatPastille, string> = {
  a_traiter: "border-border text-muted-foreground hover:bg-accent/40",
  traitee: "border-primary bg-primary text-primary-foreground",
  a_noter: "border-warning bg-warning/10 text-foreground",
  notee: "border-success bg-success/15 text-foreground",
  juste: "border-success bg-success/15 text-foreground",
  fausse: "border-destructive bg-destructive/10 text-foreground",
  non_faite: "border-dashed border-border text-muted-foreground hover:bg-accent/40",
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
  useI18n()
  const m = libellesUnite(unite)
  const LIBELLE_ETAT = libelleEtat(unite)
  // Copie rendue : seulement les états qui existent dans cette épreuve (une épreuve de QCM n'a rien « à noter »).
  const presents = new Set(groupes.flatMap((groupe) => groupe.pastilles.map((pastille) => pastille.etat)))
  const ORDRE_RENDUE: EtatPastille[] = ["juste", "fausse", "a_noter", "notee", "non_faite"]
  const legende: EtatPastille[] = rendue ? ORDRE_RENDUE.filter((etat) => presents.has(etat)) : ["traitee", "a_traiter"]

  return (
    <nav aria-label={t("pa.aria")} className="flex flex-col gap-4">
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
                  aria-label={`${t("pa.pastille_aria", { groupe: groupe.titre, unite: m.singulier, label: pastille.label, etat: LIBELLE_ETAT[pastille.etat] })}${pastille.aRevoir ? t("pa.a_revoir_suffixe") : ""}`}
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
                      className="absolute -right-1.5 -top-1.5 size-4 fill-gold text-gold-text drop-shadow-sm"
                    />
                  )}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground" aria-label={t("pa.legende")}>
        {legende.map((etat) => (
          <li key={etat} className="flex items-center gap-1.5">
            <span aria-hidden="true" className={cn("size-3 rounded border", STYLE_ETAT[etat].split(" hover")[0])} />
            {etat === "a_traiter" ? t("pa.legende_a_traiter") : LIBELLE_ETAT[etat]}
          </li>
        ))}
        {!rendue && (
          <li className="flex items-center gap-1.5">
            <Flag aria-hidden="true" className="size-3 fill-gold text-gold-text" />
            {t("pa.a_revoir")}
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
  useI18n()
  const Titre = tu("ct.palette_titre", unite)
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
          <DialogDescription>{tu("pa.touche", unite)}</DialogDescription>
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
