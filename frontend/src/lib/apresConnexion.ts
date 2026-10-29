import type { User } from "@/api/types"
import { COUNTRY_STORAGE_KEY, catalogueHomePath } from "@/lib/countryPath"
import { oublierFiltresMemorises } from "@/lib/filtresListe"
import { cheminDansLangue, memoriserLangue, type Langue } from "@/lib/i18n"
import { langueACharger, langueImposee } from "@/lib/langueProfil"

/**
 * Où l'élève atterrit juste après s'être connecté, dans quelle langue, et dans quel pays.
 *
 * Avant, la page de connexion naviguait vers le pays que le navigateur avait vu en dernier (« cm » par défaut) pendant
 * qu'un autre morceau de code rechargeait la page dans la langue du cursus - sur l'URL de la connexion, destination
 * perdue. Un élève du GCE ou du Sénégal arrivait donc sur une page de connexion déjà connecté, ou dans le mauvais pays,
 * ou dans la mauvaise langue. Tout se décide maintenant ici, en un seul endroit, à partir du compte qui vient de répondre.
 */

/** Le pays (minuscule) de l'examen que prépare le profil actif du compte, ou null sans examen déclaré. */
export function paysDuCompte(user: Pick<User, "cursus_prepare"> | null | undefined): string | null {
  return user?.cursus_prepare?.country?.code?.toLowerCase() || null
}

interface EntreeDestination {
  user: Pick<User, "cursus_prepare">
  /** Page qui a demandé la connexion (`from`), à retrouver telle quelle ; absente à l'ouverture directe de /connexion. */
  demandee?: string
  /** Pays que le navigateur affichait avant la connexion. */
  paysNavigation: string
  courante: Langue
  urlExplicite: boolean
  /** La langue imposée vient de changer pendant la session (autre profil choisi) : elle reprend la main sur un lien /en. */
  changement?: boolean
}

export function destinationApresConnexion({
  user,
  demandee,
  paysNavigation,
  courante,
  urlExplicite,
  changement = false,
}: EntreeDestination): { chemin: string; langue: Langue | null } {
  const imposee = langueImposee(user)
  return {
    // Une page précise demandée reste la destination ; sinon l'accueil du pays de l'examen de l'élève, pas du dernier
    // pays parcouru par le navigateur (un autre compte, ou une visite avant la connexion).
    chemin: demandee ?? catalogueHomePath(paysDuCompte(user) ?? paysNavigation),
    langue: imposee ? langueACharger({ imposee, courante, urlExplicite, changement }) : null,
  }
}

/**
 * Retient le pays du compte pour la prochaine ouverture de « / » (qui redirige vers le dernier pays gardé). Appelé à la
 * connexion seulement : à la restauration d'une session, le pays que l'élève a choisi de parcourir ne doit pas être écrasé.
 */
export function memoriserPaysDuCompte(user: Pick<User, "cursus_prepare">): void {
  const pays = paysDuCompte(user)
  if (!pays) return
  try {
    localStorage.setItem(COUNTRY_STORAGE_KEY, pays)
  } catch {
    /* stockage indisponible : la redirection de « / » reprendra le pays par défaut */
  }
}

/**
 * Conduit l'élève à sa destination : un rechargement direct dans la langue du cursus si elle diffère (la langue est la
 * base du routeur, fixée au chargement), sinon une navigation ordinaire. Commun à la connexion et au choix du profil.
 */
export function ouvrirDestination(
  { chemin, langue }: { chemin: string; langue: Langue | null },
  naviguer: (chemin: string, options: { replace: boolean }) => void,
): void {
  if (!langue) {
    naviguer(chemin, { replace: true })
    return
  }
  memoriserLangue(langue)
  oublierFiltresMemorises()
  window.location.assign(cheminDansLangue(chemin, langue))
}
