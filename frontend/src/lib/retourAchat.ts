import type { Cursus } from "@/api/types"

/**
 * Le chemin où ramener l'élève après un achat lancé depuis un contenu verrouillé (une épreuve
 * inédite) : transporté dans `?retour=` de /abonnement, qui survit à la connexion (voir
 * SubscribePage, qui rejoue toute sa query string) et au paiement.
 *
 * Valeur lue dans une URL que n'importe qui peut forger : seul un chemin interne est accepté,
 * jamais une adresse complète ni un `//hote` (redirection ouverte vers un site tiers).
 */
export function cheminRetourSur(valeur: string | null | undefined): string | null {
  if (!valeur || !valeur.startsWith("/")) return null
  if (valeur.startsWith("//") || valeur.includes("\\") || valeur.includes("://")) return null
  return valeur
}

/** Le cursus à acheter pour débloquer une épreuve commune à plusieurs séries : celui que
 * l'élève a déclaré préparer quand l'épreuve le couvre, sinon le premier - jamais la première
 * série venue à un élève de TI devant une épreuve « BAC D et TI ». */
export function choisirCursusPourAchat(cursus: Cursus[], declare: number | null): Cursus | undefined {
  return cursus.find((c) => c.id === declare) ?? cursus[0]
}

/** Lien vers l'abonnement « Jusqu'à l'Examen » d'un cursus, avec le chemin où revenir ensuite. */
export function lienAbonnement(cursusId: number, retour: string): string {
  const params = new URLSearchParams({ cursus: String(cursusId), duree: "examen", retour })
  return `/abonnement?${params.toString()}`
}
