import type { BilanPeriode } from "@/api/types"

/**
 * Les jalons : des paliers de travail réel (séances terminées, questions traitées, thèmes
 * devenus solides) - jamais des points ni un classement.
 *
 * Les paliers vivent ICI et non côté serveur : le serveur ne fournit que des compteurs
 * cumulés (voir BilanPeriode.jalons), ce qui permet de changer les paliers sans migration
 * ni déploiement backend. Un jalon n'est "atteint cette semaine" que si le compteur était
 * en dessous AVANT la fenêtre et est au-dessus MAINTENANT : jamais rejoué tant que
 * l'élève ne l'a pas réellement franchi.
 */

export type GenreJalon = "seances" | "questions" | "solides"

const PALIERS: Record<GenreJalon, number[]> = {
  seances: [1, 3, 5, 10, 20, 30, 50, 100],
  questions: [10, 50, 100, 250, 500, 1000],
  solides: [1, 3, 5, 10, 20, 40],
}

export interface JalonAtteint {
  genre: GenreJalon
  palier: number
  libelle: string
}

export interface ProchainJalon {
  genre: GenreJalon
  palier: number
  actuel: number
  libelle: string
  // Part du chemin déjà faite vers ce palier, 0 à 1.
  avancement: number
}

export function libelleJalon(genre: GenreJalon, palier: number): string {
  if (genre === "seances") return palier === 1 ? "Première séance terminée" : `${palier} séances terminées`
  if (genre === "questions") return `${palier} questions travaillées`
  return palier === 1 ? "Premier thème solide" : `${palier} thèmes solides`
}

function compteurs(bilan: BilanPeriode): Record<GenreJalon, { avant: number; total: number }> {
  const j = bilan.jalons
  return {
    seances: { avant: j.seances_avant, total: j.seances_total },
    questions: { avant: j.questions_avant, total: j.questions_total },
    solides: { avant: j.solides_avant, total: j.solides_total },
  }
}

/** Les paliers franchis pendant la fenêtre du bilan, le plus haut de chaque genre. */
export function jalonsAtteints(bilan: BilanPeriode): JalonAtteint[] {
  const atteints: JalonAtteint[] = []
  for (const [genre, { avant, total }] of Object.entries(compteurs(bilan)) as [GenreJalon, { avant: number; total: number }][]) {
    const franchis = PALIERS[genre].filter((palier) => avant < palier && total >= palier)
    const palier = franchis[franchis.length - 1]
    if (palier !== undefined) atteints.push({ genre, palier, libelle: libelleJalon(genre, palier) })
  }
  return atteints
}

/**
 * Le prochain palier le PLUS PROCHE d'être atteint, tous genres confondus : c'est celui qui
 * donne envie de faire "juste une séance de plus". Absent quand tout est dépassé.
 */
export function prochainJalon(bilan: BilanPeriode): ProchainJalon | null {
  let meilleur: ProchainJalon | null = null
  for (const [genre, { total }] of Object.entries(compteurs(bilan)) as [GenreJalon, { avant: number; total: number }][]) {
    const palier = PALIERS[genre].find((p) => p > total)
    if (palier === undefined) continue
    const avancement = total / palier
    if (meilleur === null || avancement > meilleur.avancement) {
      meilleur = { genre, palier, actuel: total, libelle: libelleJalon(genre, palier), avancement }
    }
  }
  return meilleur
}
