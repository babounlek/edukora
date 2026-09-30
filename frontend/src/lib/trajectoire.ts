import type { PhaseExamen, Trajectoire } from "@/api/types"
import { pourcent } from "@/lib/maitrise"

/**
 * La phrase de trajectoire (voir OuJenSuis et quiz.accueil.trajectoire) : où mène le
 * rythme actuel, dit honnêtement - rien sans rythme mesurable, "continue" quand ça
 * suffit, et sinon ce qui manque en séances par semaine, jamais un reproche.
 */
export function phraseTrajectoire(t: Trajectoire, phase: PhaseExamen): string {
  if (t.couverture_projetee === null) {
    const manque = Math.max(0, 3 - t.seances_fenetre)
    return manque > 0
      ? `Pas encore de rythme mesurable : ${manque} séance${manque > 1 ? "s" : ""} de plus et on te dit où tu vas.`
      : "Pas encore de rythme mesurable."
  }
  const projetee = pourcent(t.couverture_projetee)
  const rythme = t.seances_par_semaine === null ? "" : ` (${formatRythme(t.seances_par_semaine)})`
  if (t.suffisant) {
    if (phase === "derniere_ligne_droite" || phase === "simulation") {
      return `À ce rythme${rythme}, tu arrives le jour J avec ${projetee} % de l'essentiel. Tiens bon.`
    }
    return `À ce rythme${rythme}, tu couvres ${projetee} % de l'essentiel le jour J. Continue comme ça.`
  }
  if (t.seances_de_plus_par_semaine !== null) {
    const n = t.seances_de_plus_par_semaine
    return `À ce rythme${rythme}, tu couvres ${projetee} % de l'essentiel le jour J. ${n === 1 ? "Une séance" : `${n} séances`} de plus par semaine et tu y es.`
  }
  return `À ce rythme${rythme}, tu couvres ${projetee} % de l'essentiel le jour J. Le temps manque pour tout : vise ce qui tombe le plus.`
}

function formatRythme(parSemaine: number): string {
  const arrondi = Math.round(parSemaine * 10) / 10
  const texte = Number.isInteger(arrondi) ? String(arrondi) : String(arrondi).replace(".", ",")
  // Le pluriel commence à deux : "1,5 séance", "2 séances".
  return `${texte} séance${arrondi >= 2 ? "s" : ""} par semaine`
}

