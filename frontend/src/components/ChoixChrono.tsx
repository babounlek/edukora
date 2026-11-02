import { useEffect, useRef, useState } from "react"
import { Timer } from "lucide-react"

import { definirReglageChrono, getReglageChrono } from "@/api/endpoints"
import type { ReglageChrono } from "@/api/types"
import { PastilleFiltre } from "@/components/FiltresCatalogue"
import { formatDureeEcoulee } from "@/lib/duration"
import { t } from "@/lib/i18n"
import { dureeEstimeeSecondes } from "@/lib/quizChrono"
import { cn } from "@/lib/utils"

// Repli si le réglage n'a pas pu être chargé : mêmes valeurs que quiz.chrono côté backend. Le serveur recalcule
// la durée de toute façon, ceci n'affiche qu'une estimation.
const SECONDES_PAR_QCM_DEFAUT = 60
const TEMPS_ADDITIONNEL_DEFAUT = [0, 25, 50, 100]

/**
 * Le choix « Chronométrer ce quiz » du lancement : facultatif, refait à chaque quiz. La case est cochée
 * d'emblée si le profil l'a demandé (voir Profil.quiz_chronometres), sans jamais écraser un choix que
 * l'élève vient de faire. `indisponible` : test de niveau, où le chrono n'a pas de sens.
 */
export function ChoixChrono({
  actif, onActif, tempsAdditionnel, onTempsAdditionnel, nQuestions, indisponible,
}: {
  actif: boolean
  onActif: (valeur: boolean) => void
  tempsAdditionnel: number
  onTempsAdditionnel: (pct: number) => void
  nQuestions: number
  indisponible: boolean
}) {
  const [reglage, setReglage] = useState<ReglageChrono | null>(null)
  const [erreur, setErreur] = useState(false)
  const choisiParLEleve = useRef(false)

  useEffect(() => {
    const controle = new AbortController()
    getReglageChrono(controle.signal)
      .then((donnees) => {
        setReglage(donnees)
        if (!choisiParLEleve.current) onActif(donnees.quiz_chronometres)
      })
      // Le chrono reste utilisable sans le réglage : seule la préférence « par défaut » manque.
      .catch(() => {})
    return () => controle.abort()
    // Une seule lecture au montage : `onActif` change à chaque rendu du parent.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function basculer(valeur: boolean) {
    choisiParLEleve.current = true
    onActif(valeur)
  }

  function memoriserPreference(valeur: boolean) {
    setErreur(false)
    setReglage((courant) => (courant ? { ...courant, quiz_chronometres: valeur } : courant))
    definirReglageChrono(valeur).catch(() => {
      setReglage((courant) => (courant ? { ...courant, quiz_chronometres: !valeur } : courant))
      setErreur(true)
    })
  }

  const coche = actif && !indisponible
  const options = reglage?.temps_additionnel_possibles ?? TEMPS_ADDITIONNEL_DEFAUT
  const duree = dureeEstimeeSecondes(nQuestions, reglage?.secondes_par_qcm ?? SECONDES_PAR_QCM_DEFAUT, tempsAdditionnel)

  return (
    <div className="mt-4" data-guide="quiz-chrono">
      <label
        className={cn(
          "flex items-start gap-3 rounded-xl border px-4 py-3 transition-colors",
          indisponible ? "cursor-not-allowed opacity-60" : "cursor-pointer hover:border-primary/40",
          coche ? "border-primary bg-primary/5" : "border-border",
        )}
      >
        <input
          type="checkbox"
          checked={coche}
          disabled={indisponible}
          onChange={(e) => basculer(e.target.checked)}
          className="mt-1 size-4 shrink-0 accent-primary"
        />
        <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Timer className="size-4" aria-hidden="true" />
        </span>
        <span>
          <span className="block text-sm font-semibold">{t("chrono.option")}</span>
          <span className="block text-xs text-muted-foreground">
            {indisponible ? t("chrono.indisponible") : t("chrono.option_texte")}
          </span>
        </span>
      </label>

      {coche && (
        <div className="mt-3 pl-1">
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            {t("chrono.additionnel")}
          </p>
          <div className="flex flex-wrap gap-2">
            {options.map((pct) => (
              <PastilleFiltre key={pct} actif={tempsAdditionnel === pct} onClick={() => onTempsAdditionnel(pct)}>
                {pct === 0 ? t("chrono.normal") : t("chrono.plus", { pct })}
              </PastilleFiltre>
            ))}
          </div>
          <p className="mt-2 text-sm text-muted-foreground">
            {t("chrono.duree_allouee", { duree: formatDureeEcoulee(duree) })}
          </p>
        </div>
      )}

      {reglage && (
        <label className="mt-3 flex cursor-pointer items-center gap-2 pl-1 text-sm text-muted-foreground">
          <input
            type="checkbox"
            checked={reglage.quiz_chronometres}
            onChange={(e) => memoriserPreference(e.target.checked)}
            className="size-4 accent-primary"
          />
          {t("chrono.par_defaut")}
        </label>
      )}
      {erreur && (
        <p role="alert" className="mt-1 pl-1 text-sm text-destructive">
          {t("chrono.par_defaut_erreur")}
        </p>
      )}
    </div>
  )
}
