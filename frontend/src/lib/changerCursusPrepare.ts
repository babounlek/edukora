import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { listMySubscriptions, updateMe } from "@/api/endpoints"
import type { Cursus } from "@/api/types"
import { useAuth } from "@/context/AuthContext"

/**
 * Les cursus qu'un compte peut choisir comme examen préparé aujourd'hui : ceux où un
 * abonnement est actif - proposer de basculer vers un cursus expiré ou jamais payé
 * mènerait à une séance qui n'a rien à montrer derrière. Même clé de cache que
 * ParcoursPage (mes-abonnements) : un élève qui a déjà ouvert "Ma progression" ne
 * repaie pas cette requête pour voir le sélecteur.
 */
export function useCursusAbonnes(): Cursus[] {
  const { isAuthenticated } = useAuth()
  const { data } = useQuery({
    queryKey: ["mes-abonnements"],
    queryFn: listMySubscriptions,
    enabled: isAuthenticated,
  })
  return (data ?? []).filter((sub) => sub.is_active).map((sub) => sub.cursus)
}

/**
 * Change l'examen préparé du compte - même mutation que BandeauCursus (qui déclare un
 * premier cursus), réutilisée ici pour en changer : un compte avec deux abonnements
 * payés doit pouvoir revenir sur son choix sans se reconnecter.
 */
export function useChangerCursusPrepare() {
  const { updateUser } = useAuth()
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (cursusId: number) => updateMe({ cursus_prepare: cursusId }),
    onSuccess: (utilisateur) => {
      updateUser(utilisateur)
      // La séance du jour dépend du cursus actif : sans ça, "Aujourd'hui" continuerait
      // de montrer le plan de l'examen qu'on vient de quitter.
      queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] })
    },
  })
}
