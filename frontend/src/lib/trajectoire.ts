import type { PhaseExamen, Trajectoire } from "@/api/types"
import { pourcent } from "@/lib/maitrise"
import { langueCourante, t as tr, tn } from "@/lib/i18n"

/**
 * La phrase de trajectoire (voir OuJenSuis et quiz.accueil.trajectoire) : où mène le
 * rythme actuel, dit honnêtement - rien sans rythme mesurable, "continue" quand ça
 * suffit, et sinon ce qui manque en séances par semaine, jamais un reproche.
 */
export function phraseTrajectoire(t: Trajectoire, phase: PhaseExamen): string {
  if (t.couverture_projetee === null) {
    const manque = Math.max(0, 3 - t.seances_fenetre)
    return manque > 0 ? tn("traj.pas_de_rythme_manque", manque) : tr("traj.pas_de_rythme")
  }
  const projetee = pourcent(t.couverture_projetee)
  const rythme = t.seances_par_semaine === null ? "" : ` (${formatRythme(t.seances_par_semaine)})`
  const variables = { rythme, pct: projetee }
  // « Tu couvres 1 % de l'essentiel » le jour même d'une séance faite décourage et contredit le compteur de la semaine :
  // sous 10 %, le rythme mesuré ne dit encore rien de fiable, on le dit plutôt que de projeter un chiffre.
  if (projetee < 10) return tr("traj.debut")
  if (t.suffisant) {
    if (phase === "derniere_ligne_droite" || phase === "simulation") {
      return tr("traj.final", variables)
    }
    return tr("traj.continue", variables)
  }
  if (t.seances_de_plus_par_semaine !== null) {
    const n = t.seances_de_plus_par_semaine
    return tn("traj.plus", n, variables)
  }
  // La cible entière n'est plus à portée. Plutôt qu'un verdict (« Le temps manque pour tout », lu par un élève actif à
  // six mois de l'examen : audit des accueils, 2026-11-21), le pas suivant : ce qu'une séance de plus par semaine
  // ajoute, calculé par le serveur au même rendement (voir quiz.accueil.trajectoire). Sans gain lisible, l'ancien texte.
  const plus = t.plan?.une_seance_de_plus ? pourcent(t.plan.une_seance_de_plus.couverture_projetee) : null
  if (plus !== null && plus > projetee) return tr("traj.un_pas", { ...variables, plus })
  return tr("traj.temps_manque", variables)
}

function formatRythme(parSemaine: number): string {
  const arrondi = Math.round(parSemaine * 10) / 10
  const texte = Number.isInteger(arrondi) || langueCourante() === "en" ? String(arrondi) : String(arrondi).replace(".", ",")
  // Le pluriel commence à deux en français ("1,5 séance", "2 séances") ; en anglais "1.5 sessions".
  return tn("traj.rythme", arrondi, { texte })
}

