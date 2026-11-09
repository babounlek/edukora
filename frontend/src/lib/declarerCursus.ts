import { toast } from "sonner"

import type { Cursus } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { libelleCursus } from "@/lib/cursus"
import { useChangerCursusPrepare } from "@/lib/changerCursusPrepare"
import { memoriserCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { t } from "@/lib/i18n"

/**
 * Déclarer (ou changer) l'examen que l'on prépare, quel que soit l'endroit d'où l'on le fait : le bandeau, la ligne
 * du hero de l'accueil, la pastille de l'en-tête. Un seul chemin, pour que les trois se comportent pareil.
 *
 * Compte connecté : l'examen s'écrit sur le compte. Visiteur : il est gardé dans le navigateur (voir cursusPrepare.ts) et
 * repris à la première connexion ; un toast le confirme à l'endroit même du clic, car sans compte le seul autre effet
 * du choix est discret (listes réduites, inédites de son examen).
 */
export function useDeclarerCursus() {
  const { isAuthenticated } = useAuth()
  const changer = useChangerCursusPrepare()

  /** `apres` : appelé une fois le choix enregistré (compte) ou mémorisé (visiteur) - par exemple pour revenir à l'accueil. */
  function declarer(cursus: Cursus, apres?: () => void) {
    if (isAuthenticated) {
      changer.mutate(cursus.id, { onSuccess: apres })
      return
    }
    memoriserCursusPrepareEnAttente(cursus.id)
    toast.success(t("bandeau.note", { cursus: libelleCursus(cursus) }), {
      description: t("bandeau.connecte_toi"),
    })
    apres?.()
  }

  return { declarer, enCours: changer.isPending }
}
