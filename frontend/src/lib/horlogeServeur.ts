/**
 * Heure du serveur, pour tout ce qui se compare à une échéance qu'il a fixée (chrono d'une épreuve,
 * « il te reste… »). Un téléphone mal réglé de quelques minutes faussait sinon le temps restant :
 * le chrono s'arrêtait trop tôt ou trop tard, et les alertes de temps (« il reste 10 minutes »)
 * tombaient au mauvais moment. Le serveur reste seul juge du verrouillage ; ceci n'aligne que
 * l'affichage.
 *
 * L'écart est déduit de l'en-tête `Date` de chaque réponse (voir api/client.ts), donc sans champ
 * supplémentaire côté API. Sans réponse mesurable (en développement, API sur un autre domaine : cet
 * en-tête n'est alors pas exposé au navigateur), l'écart reste nul et l'horloge locale fait foi.
 */
let ecartMs = 0
const DELAI_MAX_MESURE_MS = 5_000

/**
 * `debut` et `fin` : instants locaux d'envoi de la requête et de réception de la réponse. L'en-tête
 * `Date` n'a qu'une précision d'une seconde (il tronque), d'où le demi-seconde ajoutée ; le serveur
 * a daté sa réponse vers le milieu de l'aller-retour, d'où le point milieu comme référence locale.
 */
export function enregistrerDateServeur(enTeteDate: string | null, debut: number, fin: number) {
  if (!enTeteDate) return
  // Une réponse lente (> 5 s) est peut-être celle d'un cache de service worker, qui garde l'en-tête
  // Date d'origine : son écart ne dit rien de l'heure actuelle. Hors connexion, jamais de mesure.
  if (fin - debut > DELAI_MAX_MESURE_MS) return
  if (typeof navigator !== "undefined" && navigator.onLine === false) return
  const serveur = Date.parse(enTeteDate)
  if (Number.isNaN(serveur)) return
  ecartMs = serveur + 500 - (debut + fin) / 2
}

/** Maintenant, à l'heure du serveur (ms depuis 1970, comme Date.now()). */
export function maintenantServeur(): number {
  return Date.now() + ecartMs
}

/** Pour les tests. */
export function reinitialiserHorlogeServeur() {
  ecartMs = 0
}
