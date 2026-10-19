import { useAuth } from "@/context/AuthContext"

/**
 * Profil actif abonné à l'examen qu'il prépare (et pas seulement un autre profil du compte) : à lui, on ne propose plus d'AUTRES examens (pastilles d'examen,
 * « résultats dans d'autres examens »...). Son accès est celui de son examen - un autre ne s'ouvrirait que sur un aperçu
 * payant - et un parent change d'enfant en changeant de profil. Visiteurs et comptes sans abonnement gardent le choix :
 * c'est ce qui les aide à décider (voir BandeauVue).
 */
export function useAbonneActif(): boolean {
  return useCursusAbonne() !== null
}

/** L'examen du profil actif quand il est abonné (voir useAbonneActif), sinon null : de quoi masquer sa puce de filtre. */
export function useCursusAbonne(): number | null {
  const { isAuthenticated, user } = useAuth()
  return isAuthenticated && user?.abonne_profil_actif && user.cursus_prepare ? user.cursus_prepare.id : null
}
