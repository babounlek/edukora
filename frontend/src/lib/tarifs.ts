import type { Plan } from "@/api/types"
import { localeCourante } from "@/lib/i18n"

/**
 * Prix affichés en dur là où aucun `Plan` n'est chargé (hero de /tarifs, paywall...). Depuis le
 * 2026-11-11, l'abonnement se vend au MOIS : 2 000 FCFA par mois, l'élève choisit combien de mois
 * (1 à `Plan.mois_max`, voir le backend). À aligner avec la table Plan côté serveur : là où un plan
 * est disponible, on lit `plan.effective_price` plutôt que ces constantes - elles ne servent qu'à ne
 * pas dupliquer le nombre d'un fichier à l'autre.
 */
export const PRIX_MOIS_FCFA = 2000
/** Un mois d'accès = 30 jours, comme côté serveur (subscriptions.models.JOURS_PAR_MOIS). */
export const JOURS_PAR_MOIS = 30
/** Durée proposée d'office quand l'élève n'en a pas encore choisi : un trimestre, ou tout ce qui reste avant l'examen. */
export const MOIS_PAR_DEFAUT = 3

/** Un plan que l'élève achète au mois (le prix du plan est celui d'UN mois). */
export function estAuMois(plan: Pick<Plan, "duration_mode">): boolean {
  return plan.duration_mode === "MENSUEL"
}

/** Ramène `mois` à ce que le plan autorise : 1 pour un plan qui ne se vend pas au mois, sinon entre 1 et `mois_max`. */
export function moisValides(plan: Pick<Plan, "duration_mode" | "mois_max">, mois: number): number {
  if (!estAuMois(plan)) return 1
  const maximum = Math.max(plan.mois_max, 1)
  // +Infinity : « tous les mois qui restent » (ancien lien duree=examen). NaN : rien de lisible, on propose un trimestre.
  if (mois === Number.POSITIVE_INFINITY) return maximum
  if (!Number.isFinite(mois)) return Math.min(MOIS_PAR_DEFAUT, maximum)
  return Math.min(Math.max(Math.round(mois), 1), maximum)
}

/**
 * Le montant TOTAL pour `mois` mois : `mois × prix du mois`. Le serveur applique la campagne
 * au prix du mois, puis multiplie (voir Plan.tarif) : ce produit est donc exactement ce qu'il facture.
 */
export function prixTotal(plan: Pick<Plan, "duration_mode" | "effective_price">, mois: number): number {
  return plan.effective_price * (estAuMois(plan) ? mois : 1)
}

/** Idem `prixTotal`, avant campagne : le prix barré. */
export function prixTotalReference(plan: Pick<Plan, "duration_mode" | "prix_reference">, mois: number): number {
  return plan.prix_reference * (estAuMois(plan) ? mois : 1)
}

/** Le jour où l'accès prend fin si l'on paie aujourd'hui `mois` mois (30 jours chacun). */
export function dateFinAcces(mois: number, depuis: Date = new Date()): Date {
  const fin = new Date(depuis)
  fin.setDate(fin.getDate() + mois * JOURS_PAR_MOIS)
  return fin
}

/** « 11 avril 2027 » dans la langue courante. */
export function formaterDateLongue(date: Date): string {
  return date.toLocaleDateString(localeCourante(), { day: "numeric", month: "long", year: "numeric" })
}
