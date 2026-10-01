import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { listMySubscriptions, updateMe } from "@/api/endpoints"
import type { Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"

/**
 * Les abonnements actifs qu'un compte peut choisir comme examen préparé aujourd'hui -
 * proposer de basculer vers un cursus expiré ou jamais payé mènerait à une séance qui
 * n'a rien à montrer derrière. Même clé de cache que ParcoursPage (mes-abonnements) :
 * un élève qui a déjà ouvert "Ma progression" ne repaie pas cette requête pour voir le
 * sélecteur.
 *
 * Renvoie l'abonnement entier (cursus + profil), pas juste le cursus : depuis
 * "Ajouter un enfant" (AccesPage.tsx), deux profils du même compte peuvent préparer le
 * MÊME cursus (deux BEPC, par ex.) - sans le profil, l'appelant ne peut plus les
 * distinguer ni les afficher sans ambiguïté (voir Header.tsx, "Examen préparé").
 */
export function useCursusAbonnes(): Subscription[] {
  const { isAuthenticated } = useAuth()
  const { data } = useQuery({
    queryKey: ["mes-abonnements"],
    queryFn: listMySubscriptions,
    enabled: isAuthenticated,
  })
  return (data ?? []).filter((sub) => sub.is_active)
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
      // de montrer le plan de l'examen qu'on vient de quitter. "progression" (voir
      // access.views.my_progression, désormais filtré par cursus_prepare) alimente
      // "Reprendre ma lecture" sur CataloguePage/CoursListPage - sans invalidation,
      // ces deux pages garderaient les lectures de l'ancien cursus jusqu'à expiration
      // du staleTime par défaut.
      queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] })
      queryClient.invalidateQueries({ queryKey: ["progression"] })
    },
  })
}
