import { useMutation, useQuery } from "@tanstack/react-query"

import { activerProfil, listProfils } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { useAuth } from "@/context/AuthContext"
import { demanderPinProfil, PinAnnule } from "@/lib/pinPrompts"

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
 * Active un profil en gérant son code PIN : si le serveur le réclame (`pin_requis`) ou
 * le refuse (`pin_incorrect`, `pin_bloque`), la saisie s'ouvre et on réessaie avec le
 * code saisi - jusqu'à réussite ou annulation (PinAnnule). Le contrôle reste côté
 * serveur : cette boucle n'est que l'interface.
 */
export async function activerProfilProtege(profilId: number, prenom: string, cursusId?: number, reverifier = false) {
  let pin: string | undefined
  for (;;) {
    try {
      return await activerProfil(profilId, cursusId, pin, reverifier)
    } catch (err) {
      const code = err instanceof ApiError ? err.code : null
      if (code !== "pin_requis" && code !== "pin_incorrect" && code !== "pin_bloque") throw err
      const saisi = await demanderPinProfil({ prenom, erreur: code === "pin_requis" ? undefined : (err as ApiError).message })
      if (saisi === null) throw new PinAnnule()
      pin = saisi
    }
  }
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
 *
 * `prenom` (optionnel) : affiché dans la saisie du code PIN du profil, s'il en a un.
 */
export function useChangerProfilActif() {
  const { login } = useAuth()
  return useMutation({
    mutationFn: ({ profilId, cursusId, prenom }: { profilId: number; cursusId?: number; prenom?: string }) =>
      activerProfilProtege(profilId, prenom ?? "ce profil", cursusId),
    onSuccess: (response) => {
      login(response.access, response.user)
      window.location.reload()
    },
    onError: (err) => {
      // Annuler la saisie du code n'est pas une erreur à signaler.
      if (err instanceof PinAnnule) return
    },
  })
}
