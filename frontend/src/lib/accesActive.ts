import type { QueryClient } from "@tanstack/react-query"

import { getMe } from "@/api/endpoints"
import type { User } from "@/api/types"

/**
 * Un accès vient de s'ouvrir : paiement CamPay confirmé, achat couvert par le crédit, ou paiement validé après coup
 * et relu au retour dans l'application (voir BandeauReprisePaiement). Le serveur sert déjà tout le contenu, mais
 * l'application gardait en mémoire le compte d'avant (`a_un_abonnement_actif`, `abonne_profil_actif`, lus par
 * l'en-tête, le catalogue, le carnet...) et les pages déjà ouvertes dans leur version verrouillée (une minute de
 * cache, voir main.tsx) : l'élève qui venait de payer voyait encore des cadenas jusqu'au rechargement.
 *
 * Les requêtes qu'aucun écran n'affiche sont retirées : la page suivante les recharge sans montrer d'abord
 * l'ancienne version verrouillée. Celles affichées en ce moment sont relues.
 */
export async function rafraichirApresActivation(queryClient: QueryClient, updateUser: (user: User) => void) {
  queryClient.removeQueries({ type: "inactive" })
  void queryClient.invalidateQueries({ type: "active" })
  try {
    updateUser(await getMe())
  } catch {
    // Le compte se relira au prochain chargement ; l'accès, lui, est déjà ouvert côté serveur.
  }
}
