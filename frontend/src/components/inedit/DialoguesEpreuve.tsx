import { Flag, Timer } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { formatDureeMinutes } from "@/lib/duration"
import { libellesUnite, compteUnite, tnu, type Unite } from "@/lib/vocabulaire"
import { t, useI18n } from "@/lib/i18n"

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
  unite?: Unite
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
  open, onOpenChange, enExamen, total, traitees, nonTraitees, aRevoir, enCours, unite = "question", onAller, onConfirmer,
}: DialogueTerminerProps) {
  useI18n()
  const vaut = nonTraitees.length
  const aller = (id: number) => {
    onOpenChange(false)
    onAller(id)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>{t("dt.titre")}</DialogTitle>
        <DialogDescription>
          {t("dt.desc_avant")}{" "}
          <strong className="text-foreground tabular-nums">{t("dt.desc_compte", { compte: compteUnite(unite, traitees), total })}</strong>.
          {enExamen && t("dt.desc_examen")}
        </DialogDescription>

        {vaut > 0 && (
          <div className="mt-4 rounded-xl border border-warning/40 bg-warning/10 px-3.5 py-3">
            <p className="text-sm font-medium">
              {tnu("dt.vaut", unite, vaut)}
            </p>
            <Reperes reperes={nonTraitees} onAller={aller} />
          </div>
        )}

        {aRevoir.length > 0 && (
          <div className="mt-3 rounded-xl border border-border px-3.5 py-3">
            <p className="flex items-center gap-1.5 text-sm font-medium">
              <Flag className="size-3.5 text-gold-text" />
              {tnu("dt.revoir", unite, aRevoir.length)}
            </p>
            <Reperes reperes={aRevoir} onAller={aller} />
          </div>
        )}

        <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("dt.continuer")}
          </Button>
          <Button disabled={enCours} onClick={onConfirmer}>
            {enCours ? t("login.envoi") : t("dt.terminer_voir")}
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
  // Voir la même note dans ChoixModeEpreuve : cette durée est déduite d'autres sessions, pas
  // celle de cette annale - dernière occasion de le dire avant de lancer un chrono qui ne
  // s'arrête plus.
  dureeEstimee?: boolean
  papier?: boolean
  enCours: boolean
  unite?: Unite
  onConfirmer: () => void
}

/** Le chrono démarre au clic et ne s'arrête plus : un bouton discret ne suffit pas pour un
 * geste irréversible, surtout quand l'élève n'a qu'à moitié lu la barre d'actions. */
export function DialogueModeExamen({
  open, onOpenChange, dureeMinutes, dureeEstimee, papier, enCours, unite = "question", onConfirmer,
}: DialogueModeExamenProps) {
  useI18n()
  const m = libellesUnite(unite)
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>{papier ? t("cm.dialogue_papier") : t("cm.dialogue_reel")}</DialogTitle>
        <DialogDescription>
          {t("cm.chrono_avant")} <strong className="text-foreground">{formatDureeMinutes(dureeMinutes)}</strong> {t("cm.chrono_apres")}
          {dureeEstimee && t("cm.duree_estimee_courte")}
        </DialogDescription>
        <ul className="mt-4 flex list-disc flex-col gap-1.5 pl-5 text-sm">
          <li>{t("cm.regle1")}</li>
          <li>{t("cm.regle2")}</li>
          <li>
            {papier
              ? t("cm.regle3_papier", { unite: m.singulier, traite: m.traite })
              : t("cm.regle3_ecran", { unite: m.singulier, traite: m.traite })}
          </li>
          <li>{t("cm.regle4")}</li>
        </ul>
        <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("cm.pas_maintenant")}
          </Button>
          <Button disabled={enCours} onClick={onConfirmer}>
            <Timer className="size-4" />
            {enCours ? t("cm.demarrage") : t("cm.lancer_chrono")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

interface DialogueQuitterProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirmer: () => void
}

/** Quitter une épreuve chronométrée n'arrête pas le chrono : mieux vaut le savoir avant de
 * fermer la page que le découvrir en revenant. Tout ce qui est déjà coché est conservé. */
export function DialogueQuitter({ open, onOpenChange, onConfirmer }: DialogueQuitterProps) {
  useI18n()
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>{t("dt.quitter_titre")}</DialogTitle>
        <DialogDescription>
          {t("dt.quitter_texte")}
        </DialogDescription>
        <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" onClick={onConfirmer}>
            {t("dt.quitter_quand_meme")}
          </Button>
          <Button onClick={() => onOpenChange(false)}>{t("dt.rester")}</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
