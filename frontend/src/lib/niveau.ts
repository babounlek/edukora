import type { NiveauXp } from "@/api/types"
import { t, type CleI18n } from "@/lib/i18n"

const NOMS: CleI18n[] = ["niveau.nom_1", "niveau.nom_2", "niveau.nom_3", "niveau.nom_4", "niveau.nom_5"]

/** Le nom du niveau d'un rang (1 à 5), dans la langue de l'interface ; un rang hors bornes retombe sur le plus proche. */
export function nomNiveau(rang: number): string {
  return t(NOMS[Math.min(Math.max(rang, 1), NOMS.length) - 1])
}

/** « Niveau 2 · Malin » */
export function libelleNiveau(niveau: NiveauXp): string {
  return t("niveau.libelle", { n: niveau.rang, nom: nomNiveau(niveau.rang) })
}

/** Part (0 à 100) du chemin entre le seuil du niveau et le suivant ; 100 au sommet. */
export function partVersSuivant(niveau: NiveauXp): number {
  if (niveau.seuil_suivant === null) return 100
  const etendue = niveau.seuil_suivant - niveau.seuil
  return etendue > 0 ? Math.min(100, Math.max(0, Math.round((100 * (niveau.xp_total - niveau.seuil)) / etendue))) : 0
}

/** Points qui manquent pour le niveau suivant, ou null au sommet. */
export function pointsRestants(niveau: NiveauXp): number | null {
  return niveau.seuil_suivant === null ? null : Math.max(0, niveau.seuil_suivant - niveau.xp_total)
}

/**
 * Le niveau qu’avait le profil AVANT un gain de `gagne` points, comparé à maintenant : vrai quand ce gain lui a fait franchir
 * un palier (sert à fêter « Nouveau niveau ! » sur l'écran de fin de quiz). Il suffit de savoir si l'XP d'avant était sous le seuil.
 */
export function aChangeDeNiveau(niveau: NiveauXp, gagne: number): boolean {
  return gagne > 0 && niveau.rang > 1 && niveau.xp_total - gagne < niveau.seuil
}
