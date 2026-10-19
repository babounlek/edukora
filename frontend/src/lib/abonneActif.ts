import { useAuth } from "@/context/AuthContext"

/**
 * Compte connecté, abonné, avec un examen préparé : à lui, on ne propose plus d'AUTRES examens (pastilles d'examen,
 * « résultats dans d'autres examens »...). Son accès est celui de son examen - un autre ne s'ouvrirait que sur un aperçu
 * payant - et un parent change d'enfant en changeant de profil. Visiteurs et comptes sans abonnement gardent le choix :
 * c'est ce qui les aide à décider (voir BandeauVue).
 */
export function useAbonneActif(): boolean {
  const { isAuthenticated, user } = useAuth()
  return Boolean(isAuthenticated && user?.a_un_abonnement_actif && user.cursus_prepare)
}
