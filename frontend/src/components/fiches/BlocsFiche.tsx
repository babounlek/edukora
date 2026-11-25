import { useState } from "react"
import { Eye, EyeOff, PencilLine, TriangleAlert } from "lucide-react"

import type { FicheEdukora } from "@/api/types"
import { NoteTexte } from "@/components/NoteTexte"
import { Button } from "@/components/ui/button"
import { t, tn, useI18n } from "@/lib/i18n"

/** Les années montrées d'emblée : au-delà, une rangée d'étiquettes repoussait la méthode sous l'écran du téléphone. */
export const ANNEES_VISIBLES = 4

/** « Tombé au BEPC 2018, 2019 » et, à part, les examens blancs : seules les sessions officielles font foi. */
export function Sessions({ fiche }: { fiche: FicheEdukora }) {
  useI18n()
  const [toutes, setToutes] = useState(false)
  const officielles = fiche.sessions.filter((s) => s.origine === "OFFICIEL").map((s) => s.annee)
  const autres = fiche.sessions.filter((s) => s.origine !== "OFFICIEL").map((s) => s.annee)
  if (officielles.length === 0 && autres.length === 0) return null
  // Les plus récentes d'abord à l'écran quand il faut choisir ; l'ordre reste chronologique.
  const triees = [...officielles].sort((a, b) => a - b)
  const repliees = toutes ? 0 : Math.max(0, triees.length - ANNEES_VISIBLES)
  return (
    <p className="flex flex-wrap items-center gap-1.5 text-xs">
      {triees.length > 0 && (
        <>
          {/* Le compte porte sur toutes les sessions, y compris les repliées. */}
          <span className="font-medium text-gold-text">{tn("fe.tombe", triees.length)}</span>
          {repliees > 0 && (
            <button
              type="button"
              onClick={() => setToutes(true)}
              aria-label={tn("fe.autres_annees", repliees)}
              className="min-h-7 rounded-full border border-gold/50 px-2 py-0.5 font-semibold tabular-nums text-gold-text hover:bg-gold/10"
            >
              +{repliees}
            </button>
          )}
          {triees.slice(repliees).map((a) => (
            <span key={a} className="rounded-full bg-gold/15 px-2 py-0.5 font-semibold tabular-nums text-gold-text">
              {a}
            </span>
          ))}
        </>
      )}
      {autres.length > 0 && (
        <span className="text-muted-foreground">{t("fe.blanc", { annees: [...new Set(autres)].join(", ") })}</span>
      )}
    </p>
  )
}

/** « À toi » : l'élève essaie d'abord, la réponse n'apparaît que s'il la demande. */
function ExerciceFiche({ exercice, reponse }: { exercice: string; reponse: string }) {
  const [montree, setMontree] = useState(false)
  return (
    <div className="mt-3 rounded-xl border border-dashed border-primary/50 bg-primary/[0.05] px-3 py-2.5">
      <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
        <PencilLine className="size-3.5" aria-hidden="true" />
        {t("fe.a_toi")}
      </p>
      <NoteTexte texte={exercice} className="mt-1" />
      {reponse && (
        <>
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="mt-2 rounded-full"
            aria-expanded={montree}
            onClick={() => setMontree((v) => !v)}
          >
            {montree ? <EyeOff /> : <Eye />}
            {t(montree ? "fe.masquer_reponse" : "fe.voir_reponse")}
          </Button>
          {montree && <NoteTexte texte={reponse} className="mt-2 border-t border-dashed border-primary/30 pt-2" />}
        </>
      )}
    </div>
  )
}

/** L'exemple, le piège et l'exercice d'une fiche, chacun dans son bloc. Un bloc vide n'est pas montré. */
export function BlocsFiche({ fiche }: { fiche: FicheEdukora }) {
  useI18n()
  return (
    <>
      {fiche.exemple && (
        <div className="mt-3 rounded-xl border-l-2 border-gold/70 bg-muted/40 px-3 py-2.5">
          <NoteTexte texte={fiche.exemple} />
        </div>
      )}
      {fiche.piege && (
        <div className="mt-3 rounded-xl border-l-2 border-warning bg-warning/10 px-3 py-2.5">
          <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-warning-foreground dark:text-warning">
            <TriangleAlert className="size-3.5" aria-hidden="true" />
            {t("fe.piege")}
          </p>
          <NoteTexte texte={fiche.piege} className="mt-1" />
        </div>
      )}
      {fiche.exercice && <ExerciceFiche exercice={fiche.exercice} reponse={fiche.reponse ?? ""} />}
    </>
  )
}
