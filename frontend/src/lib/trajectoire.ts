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
  return tr("traj.temps_manque", variables)
}

function formatRythme(parSemaine: number): string {
  const arrondi = Math.round(parSemaine * 10) / 10
  const texte = Number.isInteger(arrondi) || langueCourante() === "en" ? String(arrondi) : String(arrondi).replace(".", ",")
  // Le pluriel commence à deux en français ("1,5 séance", "2 séances") ; en anglais "1.5 sessions".
  return tn("traj.rythme", arrondi, { texte })
}

