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
 * Les abonnements actifs de l'enfant connecté, et d'eux seuls. `/mes-abonnements/` renvoie
 * ceux de tout le compte (AccesPage en a besoin pour gérer les enfants) : une page
 * personnelle (progression, parcours, quiz) qui les prendrait tels quels afficherait le
 * programme d'un frère ou d'une sœur, voire déverrouillerait un cursus qu'il n'a pas payé.
 * Sans profil connu, on rend la liste inchangée plutôt que rien.
 */
export function abonnementsActifsDuProfil(
  abonnements: Subscription[] | undefined,
  profilId: number | undefined,
): Subscription[] {
  const actifs = (abonnements ?? []).filter((sub) => sub.is_active)
  return profilId === undefined ? actifs : actifs.filter((sub) => sub.profil.id === profilId)
}

/**
 * Les abonnements que les pages personnelles (quiz, progression, parcours d'une matière)
 * proposent : celui de l'examen préparé du compte (le sélecteur « Examen préparé » du
 * bandeau, `user.cursus_prepare`), et lui seul. Un profil qui a payé deux examens (BEPC et
 * BAC C, par ex.) ne doit pas retrouver l'autre en pastille : le bandeau annonce déjà
 * l'examen visé, et changer d'examen se fait à un seul endroit.
 *
 * `cursusDemande` (lien direct `?cursus=`, posé par les boutons des autres pages) reste
 * admis, sinon un lancement depuis un autre examen que l'examen préparé tomberait dans le
 * vide. Repli : tous les abonnements quand aucun ne correspond (examen préparé non
 * déclaré, ou sans abonnement actif sur ce profil).
 */
export function abonnementsDeLExamenPrepare(
  abonnements: Subscription[],
  cursusPrepareId: number | null | undefined,
  cursusDemande: string | null = null,
): Subscription[] {
  const retenus = abonnements.filter(
    (sub) => sub.cursus.id === cursusPrepareId || String(sub.cursus.id) === cursusDemande,
  )
  return retenus.length > 0 ? retenus : abonnements
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
