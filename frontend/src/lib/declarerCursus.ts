import { toast } from "sonner"

import type { Cursus } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { libelleCursus } from "@/lib/cursus"
import { trackEvent } from "@/lib/analytics"
import { useChangerCursusPrepare } from "@/lib/changerCursusPrepare"
import { memoriserCursusPrepareEnAttente, useCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { t } from "@/lib/i18n"

/**
 * Déclarer (ou changer) l'examen que l'on prépare, quel que soit l'endroit d'où l'on le fait : le bandeau, la ligne
 * du hero de l'accueil, la pastille de l'en-tête. Un seul chemin, pour que les trois se comportent pareil.
 *
 * Compte connecté : l'examen s'écrit sur le compte. Visiteur : il est gardé dans le navigateur (voir cursusPrepare.ts) et
 * repris à la première connexion ; un toast le confirme à l'endroit même du clic, car sans compte le seul autre effet
 * du choix est discret (listes réduites, inédites de son examen).
 */
/** D'où l'examen est déclaré : vocabulaire fermé, comme les noms d'évènements. */
export type SourceChoixExamen = "bandeau" | "hero" | "selecteur"

export function useDeclarerCursus() {
  const { isAuthenticated } = useAuth()
  const changer = useChangerCursusPrepare()

  /**
   * `apres` : appelé une fois le choix enregistré (compte) ou mémorisé (visiteur) - par exemple pour revenir à l'accueil.
   * `source` : l'endroit du clic (bandeau, carte du hero de l'accueil, ou menu de l'examen choisi), pour savoir d'où les élèves déclarent
   * leur examen (audit de l'accueil du 2026-11-15, R5). Seuls la source et l'identifiant de l'examen partent.
   */
  function declarer(cursus: Cursus, apres?: () => void, source: SourceChoixExamen = "selecteur") {
    trackEvent("examen_choisi", { source, cursus_id: cursus.id })
    if (isAuthenticated) {
      changer.mutate(cursus.id, { onSuccess: apres })
      return
    }
    memoriserCursusPrepareEnAttente(cursus.id)
    // Depuis la carte du hero, pas de message : la carte affiche aussitôt l'examen choisi et sa première séance, et le
    // message recouvrait son bouton sur un téléphone.
    if (source !== "hero") {
      toast.success(t("bandeau.note", { cursus: libelleCursus(cursus) }), {
        description: t("bandeau.connecte_toi"),
      })
    }
    apres?.()
  }

  return { declarer, enCours: changer.isPending }
}

/**
 * Choisir un examen dans le filtre d'une liste vaut déclaration tant que rien n'est déclaré : le bandeau « Choisis ton
 * examen » ne s'affiche plus sur ces listes, ce filtre y pose la même question. Un élève qui a déjà déclaré le sien ne
 * fait que filtrer - regarder les épreuves d'un autre examen ne le change pas.
 */
export function useDeclarerSiRienDeclare() {
  const { isAuthenticated, user } = useAuth()
  const enAttente = useCursusPrepareEnAttente()
  const { declarer } = useDeclarerCursus()
  const aDeclare = isAuthenticated ? Boolean(user?.cursus_prepare) : enAttente !== null

  return (cursus: Cursus | undefined) => {
    if (cursus && !aDeclare) declarer(cursus, undefined, "selecteur")
  }
}
