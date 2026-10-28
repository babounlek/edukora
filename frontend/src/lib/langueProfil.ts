import type { User } from "@/api/types"
import type { Langue } from "@/lib/i18n"

/**
 * La langue de l'élève découle de son cursus : un profil qui prépare le BEPC, le Probatoire ou le BAC
 * travaille en français, un profil du GCE en anglais. Un compte famille peut ainsi porter un enfant
 * francophone et un enfant anglophone, chacun dans sa langue, la langue changeant avec le profil actif
 * (voir changerProfilActif.ts : changer de profil recharge la page).
 *
 * `user.cursus_prepare` est celui du profil actif (réaligné à chaque activation de profil côté
 * serveur), donc la langue imposée aussi. Elle ne dépend PAS de l'abonnement : un élève du GCE qui n'a
 * pas encore payé est déjà en anglais, sinon son interface changerait de langue au moment de s'abonner.
 *
 * Sans cursus déclaré (visiteur, compte neuf), rien n'est imposé : le sélecteur de langue et le choix
 * mémorisé du navigateur restent la règle.
 */
export function langueImposee(user: Pick<User, "cursus_prepare"> | null | undefined): Langue | null {
  const langue = user?.cursus_prepare?.langue
  return langue === "fr" || langue === "en" ? langue : null
}

/**
 * Le système (français / anglophone) est-il figé ? Seulement une fois le profil actif abonné à son examen :
 * jusque-là, un compte qui a déclaré un examen par curiosité ou par erreur doit pouvoir passer dans l'autre
 * système (sélecteur de langue, invitation « Tu prépares le GCE ? »). Le geste efface alors l'examen
 * déclaré, qui appartient à l'autre système (voir useChangerLangue), et le bandeau « Choisis ton examen »
 * revient avec les examens de la nouvelle langue.
 *
 * Après le premier abonnement, on change de système en changeant de profil (voir changerProfilActif.ts).
 */
export function systemeVerrouille(
  user: Pick<User, "cursus_prepare" | "abonne_profil_actif"> | null | undefined,
): boolean {
  return langueImposee(user) !== null && Boolean(user?.abonne_profil_actif)
}

interface EntreeDecision {
  /** Langue du cursus du profil actif. */
  imposee: Langue
  /** Langue de la page affichée. */
  courante: Langue
  /** La page est en anglais parce qu'un lien `/en/...` l'a demandé (voir urlAnglaiseExplicite). */
  urlExplicite: boolean
  /** La langue imposée vient de CHANGER pendant la session (nouveau cursus préparé, autre profil). */
  changement: boolean
}

/**
 * Faut-il recharger la page dans une autre langue ? Retourne la langue cible, ou null.
 *  - L'anglais est toujours imposé à un profil du GCE : une page française, ouverte par un favori ou un
 *    lien sans préfixe, passe à sa version `/en`.
 *  - Le français est imposé par défaut, mais un lien `/en/...` explicite est respecté : un élève
 *    francophone à qui un ami envoie un corrigé du GCE doit pouvoir le lire. La page le lui dit et
 *    propose la version française (voir BandeauLangueCursus). Un changement de cursus en cours de session
 *    reprend la main : il ramène bien en français.
 */
export function langueACharger({ imposee, courante, urlExplicite, changement }: EntreeDecision): Langue | null {
  if (imposee === courante) return null
  if (imposee === "en") return "en"
  return urlExplicite && !changement ? null : "fr"
}
