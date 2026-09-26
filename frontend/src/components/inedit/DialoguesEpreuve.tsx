import { Flag, Timer } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { formatDureeMinutes } from "@/lib/duration"

export interface QuestionRepere {
  id: number
  label: string
}

interface DialogueTerminerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  enExamen: boolean
  total: number
  traitees: number
  nonTraitees: QuestionRepere[]
  aRevoir: QuestionRepere[]
  enCours: boolean
  onAller: (questionId: number) => void
  onConfirmer: () => void
}

function Reperes({ reperes, onAller }: { reperes: QuestionRepere[]; onAller: (id: number) => void }) {
  return (
    <ul className="mt-2 flex flex-wrap gap-1.5">
      {reperes.map((repere) => (
        <li key={repere.id}>
          <button
            type="button"
            onClick={() => onAller(repere.id)}
            className="min-h-9 rounded-lg border border-border px-2.5 text-xs font-medium tabular-nums transition-colors hover:bg-accent/40 focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
          >
            {repere.label}
          </button>
        </li>
      ))}
    </ul>
  )
}

/** Confirmation avant de rendre l'épreuve. Elle dit ce que l'élève risque (les questions
 * non traitées valent zéro) et lui permet d'y retourner en un geste, plutôt qu'un
 * « Êtes-vous sûr ? » générique. Sauté quand tout est traité hors mode examen. */
export function DialogueTerminer({
  open, onOpenChange, enExamen, total, traitees, nonTraitees, aRevoir, enCours, onAller, onConfirmer,
}: DialogueTerminerProps) {
  const vaut = nonTraitees.length
  const aller = (id: number) => {
    onOpenChange(false)
    onAller(id)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>Terminer l'épreuve ?</DialogTitle>
        <DialogDescription>
          Tu as traité <strong className="text-foreground tabular-nums">{traitees} question{traitees > 1 ? "s" : ""} sur {total}</strong>.
          {enExamen && " Le corrigé s'ouvre dès que tu rends ta copie, et le chrono s'arrête."}
        </DialogDescription>

        {vaut > 0 && (
          <div className="mt-4 rounded-xl border border-warning/40 bg-warning/10 px-3.5 py-3">
            <p className="text-sm font-medium">
              {vaut === 1 ? "1 question non traitée vaut" : `${vaut} questions non traitées valent`} 0 point.
            </p>
            <Reperes reperes={nonTraitees} onAller={aller} />
          </div>
        )}

        {aRevoir.length > 0 && (
          <div className="mt-3 rounded-xl border border-border px-3.5 py-3">
            <p className="flex items-center gap-1.5 text-sm font-medium">
              <Flag className="size-3.5 text-gold-text" />
              {aRevoir.length === 1 ? "1 question marquée à revoir" : `${aRevoir.length} questions marquées à revoir`}
            </p>
            <Reperes reperes={aRevoir} onAller={aller} />
          </div>
        )}

        <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Continuer l'épreuve
          </Button>
          <Button disabled={enCours} onClick={onConfirmer}>
            {enCours ? "Envoi..." : "Terminer et voir le corrigé"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

interface DialogueModeExamenProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  dureeMinutes: number
  enCours: boolean
  onConfirmer: () => void
}

/** Le chrono démarre au clic et ne s'arrête plus : un bouton discret ne suffit pas pour un
 * geste irréversible, surtout quand l'élève n'a qu'à moitié lu la barre d'actions. */
export function DialogueModeExamen({ open, onOpenChange, dureeMinutes, enCours, onConfirmer }: DialogueModeExamenProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>Passer l'épreuve en conditions réelles ?</DialogTitle>
        <DialogDescription>
          Le chrono de <strong className="text-foreground">{formatDureeMinutes(dureeMinutes)}</strong> démarre tout de suite et ne
          s'arrête pas.
        </DialogDescription>
        <ul className="mt-4 flex list-disc flex-col gap-1.5 pl-5 text-sm">
          <li>Le corrigé reste masqué jusqu'à la fin de l'épreuve.</li>
          <li>À la dernière seconde, ta copie est rendue automatiquement.</li>
          <li>Compose sur brouillon ou sur papier, puis coche chaque question traitée.</li>
          <li>Tu ne pourras plus changer de mode une fois commencé.</li>
        </ul>
        <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Pas maintenant
          </Button>
          <Button disabled={enCours} onClick={onConfirmer}>
            <Timer className="size-4" />
            {enCours ? "Démarrage..." : "Lancer le chrono"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
