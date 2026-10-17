import type { AvertissementInscription, ReglesInscription } from "@/api/types"

/**
 * Écarts d'un choix de matières aux règles d'inscription du GCE Board (voir quiz.matieres.avertissements_inscription
 * côté serveur : même règle, recalculée ici pour réagir à chaque case cochée avant l'enregistrement).
 *
 * Jamais un refus : un élève peut avoir une inscription arrêtée par son établissement. Un choix vide veut dire
 * « pas encore déclaré » : aucun avertissement. `codes` = les codes des matières choisies.
 */
export function avertissementsInscription(
  regles: ReglesInscription | null | undefined,
  codes: string[],
): AvertissementInscription[] {
  if (!regles || codes.length === 0) return []
  const choisis = new Set(codes)
  const n = choisis.size
  const avertissements: AvertissementInscription[] = []
  if (regles.minimum !== null && n < regles.minimum) avertissements.push({ code: "minimum", attendu: regles.minimum, actuel: n })
  if (regles.maximum !== null && n > regles.maximum) avertissements.push({ code: "maximum", attendu: regles.maximum, actuel: n })
  for (const matiere of regles.obligatoires) {
    if (!choisis.has(matiere)) avertissements.push({ code: "obligatoire", matiere })
  }
  // Au O Level, la onzième matière doit être Religious Studies.
  if (regles.derniere && regles.maximum !== null && n >= regles.maximum && !choisis.has(regles.derniere)) {
    avertissements.push({ code: "derniere_matiere", matiere: regles.derniere })
  }
  return avertissements
}
