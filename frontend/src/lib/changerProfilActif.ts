import { useMutation, useQuery } from "@tanstack/react-query"

import { activerProfil, listProfils } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"

/**
 * Les profils (enfants) du compte - même rôle que useCursusAbonnes
 * (changerCursusPrepare.ts) pour le sélecteur d'examen, ici pour le sélecteur
 * d'enfant du menu du compte (Header.tsx).
 */
export function useProfils() {
  const { isAuthenticated } = useAuth()
  const { data } = useQuery({
    queryKey: ["mes-profils"],
    queryFn: listProfils,
    enabled: isAuthenticated,
  })
  return data ?? []
}

/**
 * Change le profil actif du compte (voir users.views.activer_profil_view) - un
 * rechargement complet suit toujours le succès plutôt qu'une invalidation React
 * Query clé par clé : changer d'enfant touche toutes les données scopées par profil
 * (séance, progression, bilan, carnet...), et un rechargement est plus sûr qu'une
 * invalidation qui en oublierait une. Basculer d'enfant reste une action déclarée et
 * peu fréquente - le coût d'un rechargement est acceptable ici, contrairement au
 * changement de cursus (useChangerCursusPrepare), bien plus fréquent.
 *
 * `cursusId` (optionnel) : voir activerProfil - à fournir dès que l'appelant sait
 * exactement quel abonnement il vise (ex. le sélecteur "Examen préparé", qui liste
 * des abonnements, pas de simples profils), jamais seulement le profil quand deux
 * cursus de ce profil pourraient tous les deux convenir au réalignement par défaut.
 */
export function useChangerProfilActif() {
  const { login } = useAuth()
  return useMutation({
    mutationFn: ({ profilId, cursusId }: { profilId: number; cursusId?: number }) =>
      activerProfil(profilId, cursusId),
    onSuccess: (response) => {
      login(response.access, response.user)
      window.location.reload()
    },
  })
}
